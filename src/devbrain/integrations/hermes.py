"""Hermes Agent: locate its home, and register devbrain in its config.yaml.

Hermes keeps its data (config.yaml, memories/, skills/, state.db) in a home
folder: $HERMES_HOME when set, otherwise %LOCALAPPDATA%\\hermes on Windows and
~/.hermes elsewhere. The program itself lives in the hermes-agent subfolder.

config.yaml is edited as text, one block at a time, so the owner's comments
and formatting survive. Every change is preceded by a timestamped backup and
followed by a YAML parse that must show exactly the intended result.
"""

from datetime import datetime
import os
from pathlib import Path
import shutil
import sys
from typing import Any, Dict, List, Optional

import yaml

from devbrain.core.constants import DIR_AGENT_SKILLS
from devbrain.core.fsutil import atomic_write_text

SERVER_NAME = "central-brain"


def hermes_home() -> Optional[Path]:
    """Hermes data folder on this machine, or None when Hermes is not installed."""
    env_home = os.getenv("HERMES_HOME")
    candidates = [Path(env_home)] if env_home else []
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        candidates.append(Path(local_appdata) / "hermes")
    candidates.append(Path.home() / ".hermes")

    for home in candidates:
        if (home / "config.yaml").is_file() and ((home / "state.db").is_file() or (home / "memories").is_dir()):
            return home
    for home in candidates:
        if (home / "config.yaml").is_file():
            return home
    return None


def server_entry(vault_path: Path) -> Dict[str, Any]:
    """Stdio command Hermes runs to start devbrain.

    Hermes passes stdio servers a filtered environment, so the variables Python
    needs to find user-installed packages and FastEmbed's model cache are set
    explicitly.
    """
    env: Dict[str, str] = {"PYTHONIOENCODING": "utf-8"}
    for key in ("APPDATA", "LOCALAPPDATA", "USERPROFILE", "HOME"):
        if os.getenv(key):
            env[key] = os.environ[key]
    cache = os.getenv("FASTEMBED_CACHE_PATH") or str(Path(os.getenv("TEMP") or "/tmp") / "fastembed_cache")
    env["FASTEMBED_CACHE_PATH"] = cache
    return {
        "command": sys.executable.replace("\\", "/"),
        "args": ["-m", "devbrain.cli.main", "serve", "--stdio", "--no-watch", "--vault", str(Path(vault_path).resolve())],
        "env": env,
        "connect_timeout": 120,
        "enabled": True,
    }


def _q(value: str) -> str:
    """Quote a scalar for YAML (JSON strings are valid YAML)."""
    import json

    return json.dumps(value, ensure_ascii=False)


def _render_server_block(entry: Dict[str, Any]) -> List[str]:
    lines = [f"  {SERVER_NAME}:", f"    command: {_q(entry['command'])}", "    args:"]
    lines += [f"      - {_q(arg)}" for arg in entry["args"]]
    lines.append("    env:")
    lines += [f"      {key}: {_q(value)}" for key, value in entry["env"].items()]
    lines += [f"    connect_timeout: {entry['connect_timeout']}", "    enabled: true"]
    return lines


def _top_level_block(lines: List[str], key: str) -> Optional[tuple]:
    """(start, end) line indexes of a top-level YAML key's block; end is exclusive."""
    start = next((i for i, l in enumerate(lines) if l.rstrip() == f"{key}:" or l.startswith(f"{key}: ")), None)
    if start is None:
        return None
    end = start + 1
    while end < len(lines) and (lines[end].startswith((" ", "\t")) or not lines[end].strip()):
        end += 1
    # Trailing blank lines belong to whatever follows
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    return start, end


def _child_block(lines: List[str], parent: tuple, child: str) -> Optional[tuple]:
    """(start, end) of a two-space-indented child key inside a top-level block."""
    start, end = parent
    begin = next((i for i in range(start + 1, end) if lines[i].startswith(f"  {child}:")), None)
    if begin is None:
        return None
    stop = begin + 1
    while stop < end and (lines[stop].startswith("    ") or not lines[stop].strip()):
        stop += 1
    while stop > begin + 1 and not lines[stop - 1].strip():
        stop -= 1
    return begin, stop


def _backup(config: Path) -> Path:
    backup = config.with_name(f"config.yaml.devbrain-bak-{datetime.now():%Y%m%d_%H%M%S}")
    shutil.copy2(config, backup)
    return backup


def _apply(config: Path, lines: List[str], check) -> Path:
    """Validate the edited text, back up the original, then write the edit."""
    text = "\n".join(lines) + "\n"
    data = yaml.safe_load(text)
    if not isinstance(data, dict) or not check(data):
        raise RuntimeError("Edited Hermes config did not parse to the expected result; nothing was written.")
    backup = _backup(config)
    atomic_write_text(config, text)
    return backup


def connect(vault_path: Path, home: Path, share_skills: bool = True) -> Dict[str, Any]:
    """Register devbrain as an MCP server in Hermes and, optionally, share the vault's skills.

    Skills are shared read-only, through skills.external_dirs; Hermes still
    writes the skills it creates into its own home.
    """
    config = home / "config.yaml"
    lines = config.read_text(encoding="utf-8").splitlines()
    entry = server_entry(vault_path)
    skills_dir = str((Path(vault_path) / DIR_AGENT_SKILLS).resolve()).replace("\\", "/")

    # MCP server: replace an existing central-brain block or add one
    servers = _top_level_block(lines, "mcp_servers")
    if servers is None:
        lines += ["", "mcp_servers:", *_render_server_block(entry)]
    elif lines[servers[0]].strip() in ("mcp_servers: {}", "mcp_servers: null"):
        lines[servers[0]: servers[0] + 1] = ["mcp_servers:", *_render_server_block(entry)]
    else:
        existing = _child_block(lines, servers, SERVER_NAME)
        if existing:
            lines[existing[0]: existing[1]] = _render_server_block(entry)
        else:
            lines[servers[1]: servers[1]] = _render_server_block(entry)

    # Shared skills: add the vault's skill folder to skills.external_dirs
    if share_skills:
        skills = _top_level_block(lines, "skills")
        current = (yaml.safe_load("\n".join(lines)) or {}).get("skills") or {}
        dirs = [str(d) for d in (current.get("external_dirs") or [])]
        if skills_dir not in dirs:
            dirs.append(skills_dir)
        new_line = f"  external_dirs: [{', '.join(_q(d) for d in dirs)}]"
        if skills is None:
            lines += ["", "skills:", new_line]
        else:
            child = _child_block(lines, skills, "external_dirs")
            if child:
                lines[child[0]: child[1]] = [new_line]
            else:
                lines[skills[0] + 1: skills[0] + 1] = [new_line]

    def check(data: dict) -> bool:
        ok = (data.get("mcp_servers") or {}).get(SERVER_NAME) == entry
        if share_skills:
            ok = ok and skills_dir in ((data.get("skills") or {}).get("external_dirs") or [])
        return ok

    backup = _apply(config, lines, check)
    return {"config": config, "backup": backup, "skills_dir": skills_dir if share_skills else None, "entry": entry}


def disconnect(home: Path, vault_path: Optional[Path] = None) -> Dict[str, Any]:
    """Remove devbrain's MCP entry and the vault's skill folder from Hermes' config."""
    config = home / "config.yaml"
    lines = config.read_text(encoding="utf-8").splitlines()
    changed = False

    servers = _top_level_block(lines, "mcp_servers")
    existing = _child_block(lines, servers, SERVER_NAME) if servers else None
    if existing:
        del lines[existing[0]: existing[1]]
        changed = True

    skills_dir = None
    if vault_path:
        skills_dir = str((Path(vault_path) / DIR_AGENT_SKILLS).resolve()).replace("\\", "/")
        skills = _top_level_block(lines, "skills")
        current = (yaml.safe_load("\n".join(lines)) or {}).get("skills") or {}
        dirs = [str(d) for d in (current.get("external_dirs") or [])]
        if skills and skills_dir in dirs:
            dirs.remove(skills_dir)
            child = _child_block(lines, skills, "external_dirs")
            lines[child[0]: child[1]] = [f"  external_dirs: [{', '.join(_q(d) for d in dirs)}]"]
            changed = True

    if not changed:
        return {"config": config, "backup": None}

    def check(data: dict) -> bool:
        ok = SERVER_NAME not in (data.get("mcp_servers") or {})
        if skills_dir:
            ok = ok and skills_dir not in ((data.get("skills") or {}).get("external_dirs") or [])
        return ok

    return {"config": config, "backup": _apply(config, lines, check)}


def status(home: Path) -> Dict[str, Any]:
    data = yaml.safe_load((home / "config.yaml").read_text(encoding="utf-8")) or {}
    return {
        "server": (data.get("mcp_servers") or {}).get(SERVER_NAME),
        "external_dirs": (data.get("skills") or {}).get("external_dirs") or [],
        "write_approval": {
            "memory": (data.get("memory") or {}).get("write_approval", False),
            "skills": (data.get("skills") or {}).get("write_approval", False),
        },
    }
