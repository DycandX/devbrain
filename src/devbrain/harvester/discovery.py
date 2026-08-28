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
        "antigravity": [
            home / ".gemini" / "antigravity-ide" / "brain",
            home / ".gemini" / "antigravity" / "brain",
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

    target_sources = sources if sources and "all" not in sources else list(agent_roots.keys())

    for src in target_sources:
        candidate_paths = agent_roots.get(src, [])
        for root in candidate_paths:
            if not root.is_dir():
                continue

            if src == "antigravity":
                # Antigravity sessions are subfolders with UUID or project names under brain/
                for session_dir in root.iterdir():
                    if session_dir.is_dir() and not session_dir.name.startswith("."):
                        artifacts = []
                        for filename in ["walkthrough.md", "implementation_plan.md", "task.md"]:
                            cand = session_dir / filename
                            if cand.is_file():
                                artifacts.append(cand)

                        # Also check transcript.jsonl
                        log_cand = session_dir / ".system_generated" / "logs" / "transcript.jsonl"
                        if log_cand.is_file():
                            artifacts.append(log_cand)

                        if artifacts:
                            latest_mtime = max(f.stat().st_mtime for f in artifacts)
                            discovered.append(
                                HarvestableSession(
                                    session_id=session_dir.name,
                                    source_name="antigravity",
                                    root_path=session_dir,
                                    artifact_files=artifacts,
                                    last_modified=latest_mtime,
                                )
                            )

            elif src == "claude-code":
                # Claude Code projects contain session files / json logs
                for proj_dir in root.iterdir():
                    if proj_dir.is_dir():
                        json_files = list(proj_dir.glob("*.jsonl")) + list(proj_dir.glob("*.json"))
                        if json_files:
                            latest_mtime = max(f.stat().st_mtime for f in json_files)
                            discovered.append(
                                HarvestableSession(
                                    session_id=proj_dir.name,
                                    source_name="claude-code",
                                    root_path=proj_dir,
                                    artifact_files=json_files,
                                    last_modified=latest_mtime,
                                )
                            )

            elif src == "cline":
                # Cline tasks contain api_conversation_history.json
                for task_dir in root.iterdir():
                    if task_dir.is_dir():
                        history_file = task_dir / "api_conversation_history.json"
                        if history_file.is_file():
                            discovered.append(
                                HarvestableSession(
                                    session_id=task_dir.name,
                                    source_name="cline",
                                    root_path=task_dir,
                                    artifact_files=[history_file],
                                    last_modified=history_file.stat().st_mtime,
                                )
                            )

    # Sort discovered sessions chronologically (newest first)
    discovered.sort(key=lambda s: s.last_modified, reverse=True)
    return discovered
