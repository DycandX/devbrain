"""Frontmatter schema shared by every note devbrain writes or checks."""

from pathlib import PurePosixPath
from typing import Optional

from devbrain.core.constants import (
    DIR_AGENT_SKILLS,
    DIR_DAILY,
    DIR_DECISIONS,
    DIR_INBOX,
    DIR_KNOWLEDGE,
    DIR_MEMORIES,
    DIR_PROJECTS,
    DIR_SYSTEM,
)

REQUIRED_KEYS = ("type", "title", "created", "tags")
OPTIONAL_KEYS = ("updated", "project", "status", "aliases", "group", "sandbox")

# Older notes carry their creation time under one of these keys.
CREATED_FALLBACK_KEYS = ("date", "updated", "last_scanned")

# Folders whose notes follow another format (skills use the agentskills.io
# SKILL.md frontmatter: name, description).
SCHEMA_EXEMPT_DIRS = (DIR_AGENT_SKILLS,)


def infer_note_type(rel_path: str) -> Optional[str]:
    """Note type implied by where a note lives in the vault taxonomy."""
    path = PurePosixPath(rel_path)
    name = path.name
    if name.startswith("_") and name.endswith("_Index.md"):
        return "index-hub"

    folder = path.as_posix()
    if folder.startswith(f"{DIR_MEMORIES}/"):
        return "memory"
    if folder.startswith(f"{DIR_SYSTEM}/"):
        return "system-context"
    if folder.startswith(f"{DIR_PROJECTS}/"):
        return "project"
    if folder.startswith(f"{DIR_KNOWLEDGE}/"):
        return "knowledge-doc"
    if folder.startswith(f"{DIR_DECISIONS}/"):
        return "adr"
    if folder.startswith(f"{DIR_INBOX}/"):
        return "agent-session-log"
    if folder.startswith(f"{DIR_DAILY}/"):
        return "daily"
    return None


def is_schema_exempt(rel_path: str) -> bool:
    return any(rel_path.startswith(f"{d}/") for d in SCHEMA_EXEMPT_DIRS)
