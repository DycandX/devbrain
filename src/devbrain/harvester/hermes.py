"""Read Hermes Agent sessions and core memory (read-only) for ingestion into the vault.

Sessions come from Hermes' state.db, opened in read-only mode so a running
Hermes gateway is never blocked or modified. The core memory files
(memories/MEMORY.md, memories/USER.md) are mirrored into one vault note.
"""

import json
from pathlib import Path
import sqlite3
from typing import List, Optional

from devbrain.harvester.claude_code import ClaudeSessionSummary
from devbrain.harvester.discovery import HarvestableSession

# Hermes separates core memory entries with this character.
ENTRY_SEPARATOR = "§"


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def discover_hermes_sessions(home: Path) -> List[HarvestableSession]:
    """Every Hermes session that has messages, newest activity first."""
    db_path = home / "state.db"
    if not db_path.is_file():
        return []
    try:
        conn = _connect(db_path)
        try:
            rows = conn.execute(
                "SELECT id, started_at, ended_at, last_activity_at FROM sessions WHERE message_count > 0"
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return []

    sessions = [
        HarvestableSession(
            session_id=row["id"],
            source_name="hermes",
            root_path=home,
            artifact_files=[db_path],
            last_modified=float(row["last_activity_at"] or row["ended_at"] or row["started_at"] or 0),
        )
        for row in rows
    ]
    sessions.sort(key=lambda s: s.last_modified, reverse=True)
    return sessions


def parse_hermes_session(db_path: Path, session_id: str) -> Optional[tuple]:
    """(summary, title, channel) for one session, or None when it has no user message."""
    conn = _connect(db_path)
    try:
        meta = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if meta is None:
            return None
        messages = conn.execute(
            "SELECT role, content, tool_name FROM messages WHERE session_id = ? ORDER BY id", (session_id,)
        ).fetchall()
    finally:
        conn.close()

    summary = ClaudeSessionSummary(session_id=session_id, cwd=meta["cwd"], git_branch=meta["git_branch"])
    for msg in messages:
        content = (msg["content"] or "").strip()
        if msg["role"] == "user" and content:
            summary.user_prompts.append(" ".join(content.split()))
        elif msg["role"] == "assistant":
            summary.assistant_messages += 1
            if content:
                summary.final_answer = content
        elif msg["role"] == "tool" and msg["tool_name"]:
            summary.tool_calls[msg["tool_name"]] = summary.tool_calls.get(msg["tool_name"], 0) + 1

    if not summary.user_prompts:
        return None

    summary.usage = {
        "input_tokens": int(meta["input_tokens"] or 0),
        "output_tokens": int(meta["output_tokens"] or 0),
        "cache_read_input_tokens": int(meta["cache_read_tokens"] or 0),
        "cache_creation_input_tokens": int(meta["cache_write_tokens"] or 0),
    }
    channel = meta["display_name"] or meta["source"]
    return summary, meta["title"], f"{meta['source']}: {channel}" if meta["display_name"] else meta["source"]


def read_core_memory(home: Path) -> dict:
    """Hermes' bounded core memory: {"memory": [...], "user": [...]} entries."""
    result = {}
    for key, name in (("memory", "MEMORY.md"), ("user", "USER.md")):
        path = home / "memories" / name
        text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
        result[key] = [e.strip() for e in text.split(ENTRY_SEPARATOR) if e.strip()]
    return result


def render_core_memory_note(memory: dict, home: Path, updated: str) -> str:
    """Vault note mirroring Hermes' core memory. Rewritten whenever it changes."""
    def section(entries: List[str]) -> str:
        return "\n".join(f"- {' '.join(e.split())}" for e in entries) or "- (kosong)"

    return (
        "---\n"
        'type: "system-context"\n'
        'title: "Hermes Core Memory"\n'
        f"created: {json.dumps(updated)}\n"
        f"updated: {json.dumps(updated)}\n"
        'source: "hermes"\n'
        'tags: ["hermes", "agent-memory"]\n'
        "---\n\n"
        "# Hermes Core Memory\n\n"
        f"> Salinan otomatis dari `{home.as_posix()}/memories/`. Jangan diedit di sini; Hermes yang mengelolanya.\n\n"
        f"## Tentang Pengguna (USER.md)\n{section(memory['user'])}\n\n"
        f"## Catatan Agent (MEMORY.md)\n{section(memory['memory'])}\n"
    )
