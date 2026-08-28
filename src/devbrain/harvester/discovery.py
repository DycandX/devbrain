"""Dynamic Multi-Agent Storage Discovery Engine."""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class HarvestableSession:
    """Represents a discovered agent session directory or file ready for ingestion."""
    session_id: str
    source_name: str
    root_path: Path
    artifact_files: List[Path]
    last_modified: float


def get_default_agent_roots() -> Dict[str, List[Path]]:
    """Resolve potential agent session root directories across operating systems."""
    home = Path.home()
    appdata_raw = os.getenv("APPDATA")
    appdata = Path(appdata_raw) if appdata_raw else home / "AppData" / "Roaming"

    roots = {
        "antigravity-ide": [
            home / ".gemini" / "antigravity-ide" / "brain",
            home / ".gemini" / "antigravity" / "brain",
        ],
        "antigravity-cli": [
            home / ".gemini" / "antigravity-cli" / "brain",
            home / ".gemini" / "agy" / "brain",
            home / ".gemini" / "antigravity-cli",
        ],
        "claude-code": [
            home / ".claude" / "projects",
        ],
        "cline": [
            appdata / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "tasks",
            home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "tasks",
            home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "tasks",
        ],
    }
    return roots


def discover_sessions(
    sources: Optional[List[str]] = None,
    custom_paths: Optional[Dict[str, Path]] = None,
) -> List[HarvestableSession]:
    """Scan the system for completed AI agent sessions ready for ingestion."""
    discovered: List[HarvestableSession] = []
    agent_roots = get_default_agent_roots()

    if custom_paths:
        for src, p in custom_paths.items():
            paths = [p] if isinstance(p, Path) else list(p)
            agent_roots[src] = paths

    # Expand source filters (e.g. 'antigravity' matches 'antigravity-ide' and 'antigravity-cli')
    target_sources = []
    if sources and "all" not in sources:
        for s in sources:
            s_clean = s.strip().lower()
            matched = [k for k in agent_roots.keys() if k == s_clean or k.startswith(s_clean)]
            if matched:
                target_sources.extend(matched)
            else:
                target_sources.append(s_clean)
        target_sources = list(set(target_sources))
    else:
        target_sources = list(agent_roots.keys())

    for src in target_sources:
        candidate_paths = agent_roots.get(src, [])
        for root in candidate_paths:
            if not root.is_dir():
                continue

            try:
                # 1. Antigravity IDE & Antigravity CLI structure
                if src.startswith("antigravity"):
                    for session_dir in root.iterdir():
                        if session_dir.is_dir():
                            # Check if valid session
                            has_wt = (session_dir / "walkthrough.md").is_file()
                            has_plan = (session_dir / "implementation_plan.md").is_file()
                            has_log = (session_dir / ".system_generated" / "logs" / "transcript.jsonl").is_file()

                            if has_wt or has_plan or has_log:
                                artifacts = [p for p in session_dir.glob("*.md") if p.is_file()]
                                mtime = session_dir.stat().st_mtime
                                discovered.append(
                                    HarvestableSession(
                                        session_id=session_dir.name,
                                        source_name=src,
                                        root_path=session_dir,
                                        artifact_files=artifacts,
                                        last_modified=mtime,
                                    )
                                )

                # 2. Claude Code structure
                elif src == "claude-code":
                    for project_dir in root.iterdir():
                        if project_dir.is_dir():
                            logs = list(project_dir.glob("*.jsonl")) + list(project_dir.glob("*.json"))
                            if logs:
                                mtime = max(p.stat().st_mtime for p in logs)
                                discovered.append(
                                    HarvestableSession(
                                        session_id=project_dir.name,
                                        source_name="claude-code",
                                        root_path=project_dir,
                                        artifact_files=logs,
                                        last_modified=mtime,
                                    )
                                )

                # 3. Cline / Roo Code structure
                elif src == "cline":
                    for task_dir in root.iterdir():
                        if task_dir.is_dir():
                            task_files = list(task_dir.glob("*.json"))
                            if task_files:
                                mtime = max(p.stat().st_mtime for p in task_files)
                                discovered.append(
                                    HarvestableSession(
                                        session_id=task_dir.name,
                                        source_name="cline",
                                        root_path=task_dir,
                                        artifact_files=task_files,
                                        last_modified=mtime,
                                    )
                                )
            except PermissionError:
                continue
            except Exception:
                continue

    # Sort descending by last modified time (newest first)
    discovered.sort(key=lambda s: s.last_modified, reverse=True)
    return discovered
