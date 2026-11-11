"""Claude Code hooks: brief the agent when a session starts, harvest the session when it ends.

Hooks are installed per project, in <project>/.claude/settings.local.json (a
machine-specific file Claude Code keeps out of version control), so a project
opts in explicitly. Each hook runs `python -m devbrain.cli.main hooks run <event>`.

SessionStart prints a compact briefing as additional context: project card
summary, core memory, the project's memories, active decisions, and recent
sessions. It reads only files and SQLite, never the embedding model, so it
starts fast. SessionEnd starts a detached harvest of Claude Code sessions so
closing the session is not delayed.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, Dict, List, Optional

from devbrain.context.builder import ContextAssemblyEngine
from devbrain.core.constants import DIR_PROJECTS
from devbrain.core.fsutil import atomic_write_json
from devbrain.core.sqlite_db import BrainSQLiteStorage
from devbrain.core.textutil import truncate_to_budget
from devbrain.engine.parser import parse_frontmatter

HOOK_MARKER = "devbrain.cli.main hooks run"
SETTINGS_FILE = Path(".claude") / "settings.local.json"
BRIEFING_MAX_CHARS = 5000
PROJECT_MEMORY_LIMIT = 8
HOOK_TIMEOUT_SECONDS = 30


# --- Install ---------------------------------------------------------------


def hook_command(event: str, vault_path: Path) -> str:
    python = sys.executable.replace("\\", "/")
    return f'"{python}" -m {HOOK_MARKER} {event} --vault "{Path(vault_path).resolve().as_posix()}"'


def _settings_path(project_dir: Path) -> Path:
    return Path(project_dir).resolve() / SETTINGS_FILE


def _read_settings(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8") or "{}")
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not hold a JSON object.")
    return data


def _without_devbrain(groups: List[dict]) -> List[dict]:
    """Hook groups with devbrain's own commands removed; empty groups dropped."""
    kept = []
    for group in groups:
        hooks = [h for h in group.get("hooks", []) if HOOK_MARKER not in str(h.get("command", ""))]
        if hooks:
            kept.append({**group, "hooks": hooks})
    return kept


def install(project_dir: Path, vault_path: Path) -> Path:
    """Add devbrain's SessionStart and SessionEnd hooks to a project, replacing older ones."""
    path = _settings_path(project_dir)
    settings = _read_settings(path)
    hooks = settings.setdefault("hooks", {})
    for event, arg in (("SessionStart", "session-start"), ("SessionEnd", "session-end")):
        groups = _without_devbrain(hooks.get(event, []))
        groups.append({"hooks": [{"type": "command", "command": hook_command(arg, vault_path), "timeout": HOOK_TIMEOUT_SECONDS}]})
        hooks[event] = groups
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(path, settings)
    return path


def uninstall(project_dir: Path) -> bool:
    """Remove devbrain's hooks from a project; other hooks and settings stay."""
    path = _settings_path(project_dir)
    settings = _read_settings(path)
    hooks = settings.get("hooks") or {}
    changed = False
    for event in list(hooks):
        kept = _without_devbrain(hooks[event])
        if kept != hooks[event]:
            changed = True
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    if not changed:
        return False
    if not hooks:
        settings.pop("hooks", None)
    atomic_write_json(path, settings)
    return True


def installed_events(project_dir: Path) -> List[str]:
    hooks = _read_settings(_settings_path(project_dir)).get("hooks") or {}
    return [e for e, groups in hooks.items() if any(HOOK_MARKER in str(h.get("command", "")) for g in groups for h in g.get("hooks", []))]


# --- Run -------------------------------------------------------------------


def find_project_for_path(vault_path: Path, cwd: str) -> Optional[str]:
    """Name of the project card whose local_path contains cwd (deepest match wins)."""
    target = cwd.replace("\\", "/").rstrip("/").lower()
    best, best_len = None, -1
    for card in (Path(vault_path) / DIR_PROJECTS).glob("*/README.md"):
        try:
            meta, _ = parse_frontmatter(card.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        local = str(meta.get("local_path") or "").replace("\\", "/").rstrip("/").lower()
        if local and (target == local or target.startswith(local + "/")) and len(local) > best_len:
            best, best_len = card.parent.name, len(local)
    return best


def session_start_context(vault_path: Path, cwd: str) -> Optional[str]:
    """Briefing text for a session starting in cwd, or None outside any known project."""
    project = find_project_for_path(vault_path, cwd)
    if project is None:
        return None

    sqlite = BrainSQLiteStorage(vault_path)
    core = [m["content"] for m in sqlite.get_pinned_memories(project)]
    core_set = set(core)
    project_memories = [
        m["content"]
        for m in sqlite.get_memories(scope="PROJECT", project=project)
        if m["project"] == project and m["content"] not in core_set
    ][:PROJECT_MEMORY_LIMIT]

    card = ContextAssemblyEngine(vault_path, sqlite).build_task_context(
        task="(sesi baru; tugas belum diketahui)",
        project=project,
        relevant_chunks=[],
        memories=project_memories,
        core_memories=core,
    )
    briefing = truncate_to_budget(card.to_markdown(), BRIEFING_MAX_CHARS, "Panggil build_task_context untuk briefing lengkap.")
    return (
        f"{briefing}\n\n"
        "**DevBrain:** Sebelum mengakhiri pekerjaan, simpan fakta yang perlu diingat sesi berikutnya dengan "
        f'`remember(content, scope="PROJECT", project="{project}")`; satu fakta per panggilan. '
        "Untuk tugas tertentu, panggil `build_task_context(task, project)`."
    )


def run_session_start(payload: Dict[str, Any], vault_path: Path) -> str:
    """Hook output (JSON) for SessionStart; empty when the folder is not a known project."""
    context = session_start_context(vault_path, payload.get("cwd") or os.getcwd())
    if not context:
        return ""
    return json.dumps(
        {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}},
        ensure_ascii=True,
    )


def _spawn_detached(args: List[str]) -> None:
    flags = 0
    if os.name == "nt":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    subprocess.Popen(
        args,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
        close_fds=True,
    )


def run_session_end(
    payload: Dict[str, Any],
    vault_path: Path,
    spawn: Callable[[List[str]], None] = _spawn_detached,
) -> List[str]:
    """Start a background harvest of Claude Code sessions. Returns the command started."""
    args = [sys.executable, "-m", "devbrain.cli.main", "ingest", "--from", "claude-code", "--vault", str(Path(vault_path).resolve())]
    spawn(args)
    return args
