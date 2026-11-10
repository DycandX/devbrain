"""Long-term memory: facts and preferences an agent chooses to keep across sessions.

SQLite (.brain_data/brain.db) is the record of every memory and its lifecycle.
Each active memory is mirrored as a Markdown note in 00_System/Memories/, which
makes it visible in Obsidian and searchable through the hybrid engine. Memories
that are superseded or forgotten keep their SQLite row and lose their note, so
recall only ever sees active ones.
"""

import json
from pathlib import Path
from typing import Any, Optional

from devbrain.core.constants import DIR_MEMORIES
from devbrain.core.fsutil import atomic_write_text
from devbrain.core.sqlite_db import BrainSQLiteStorage
from devbrain.engine.hybrid_search import HybridEngine

MEMORY_SCOPES = ("GLOBAL", "PROJECT", "TASK", "SESSION")
MAX_MEMORY_CHARS = 1000


class MemoryManager:
    """Write, retrieve, and retire memories."""

    def __init__(
        self,
        vault_path: Path,
        sqlite_storage: Optional[BrainSQLiteStorage] = None,
        engine: Optional[HybridEngine] = None,
    ):
        self.vault_path = Path(vault_path).resolve()
        self.sqlite = sqlite_storage or BrainSQLiteStorage(self.vault_path)
        self.engine = engine or HybridEngine.from_config(self.vault_path)
        self.notes_dir = self.vault_path / DIR_MEMORIES

    # --- Write -------------------------------------------------------------

    def remember(
        self,
        content: str,
        scope: str = "GLOBAL",
        project: Optional[str] = None,
        memory_type: str = "fact",
        tags: Optional[list[str]] = None,
        source: Optional[str] = None,
        supersedes: Optional[str] = None,
    ) -> dict[str, Any]:
        """Store a memory. Returns {"id", "created", "superseded"}.

        Remembering text that is already an active memory returns the existing
        id instead of storing a duplicate.
        """
        content = " ".join(content.split())
        if not content:
            raise ValueError("Memory content is empty.")
        if len(content) > MAX_MEMORY_CHARS:
            raise ValueError(
                f"Memory is {len(content)} characters; keep it under {MAX_MEMORY_CHARS}. "
                "Store one fact per memory, or write a note for longer material."
            )

        scope = scope.upper()
        if scope not in MEMORY_SCOPES:
            raise ValueError(f"Unknown scope '{scope}'. Use one of: {', '.join(MEMORY_SCOPES)}.")
        if scope == "PROJECT" and not project:
            raise ValueError("A PROJECT-scoped memory needs a project name.")

        existing = self.sqlite.find_active_memory(content, project)
        if existing:
            return {"id": existing["id"], "created": False, "superseded": None}

        memory_id = self.sqlite.upsert_memory(
            content=content,
            type=memory_type,
            scope=scope,
            project=project,
            source=source,
            metadata={"tags": tags or []},
        )
        self._write_note(memory_id, content, scope, project, memory_type, tags or [])

        superseded = None
        if supersedes and self.sqlite.supersede_memory(supersedes, memory_id):
            self._delete_note(supersedes)
            superseded = supersedes

        self.engine.index_vault()
        return {"id": memory_id, "created": True, "superseded": superseded}

    def forget(self, memory_id: str) -> bool:
        """Retire a memory. Its row is kept with status 'forgotten'; its note is removed."""
        if not self.sqlite.set_memory_status(memory_id, "forgotten"):
            return False
        self._delete_note(memory_id)
        self.engine.index_vault()
        return True

    # --- Read --------------------------------------------------------------

    def recall(
        self,
        query: str = "",
        project: Optional[str] = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Return active memories relevant to the query, most relevant first.

        With a project, memories of that project and global ones are eligible.
        Without a query, the most recently updated memories are returned.
        """
        if not query.strip():
            return self.sqlite.get_memories(project=project)[:limit]

        hits = self.engine.search(query, limit=limit * 3, scope=DIR_MEMORIES.lower())
        results: list[dict[str, Any]] = []
        seen: set[str] = set()
        for hit in hits:
            memory_id = Path(hit.file_path).stem
            if memory_id in seen:
                continue
            seen.add(memory_id)

            memory = self.sqlite.get_memory(memory_id)
            if not memory or memory["status"] != "active":
                continue
            if project and memory["project"] not in (None, project):
                continue

            memory["score"] = hit.score
            results.append(memory)
            if len(results) >= limit:
                break
        return results

    # --- Markdown mirror ---------------------------------------------------

    def _note_path(self, memory_id: str) -> Path:
        return self.notes_dir / f"{memory_id}.md"

    def _write_note(
        self,
        memory_id: str,
        content: str,
        scope: str,
        project: Optional[str],
        memory_type: str,
        tags: list[str],
    ) -> None:
        all_tags = ["memory", scope.lower(), *tags]
        frontmatter = [
            "---",
            f'id: "{memory_id}"',
            "type: memory",
            f"memory_type: {json.dumps(memory_type)}",
            f"scope: {scope}",
        ]
        if project:
            frontmatter.append(f"project: {json.dumps(project, ensure_ascii=False)}")
        frontmatter += [f"tags: {json.dumps(all_tags, ensure_ascii=False)}", "---", ""]

        project_link = f"\n\nProject: [[{project}]]" if project else ""
        atomic_write_text(
            self._note_path(memory_id),
            "\n".join(frontmatter) + f"# Memory {memory_id}\n\n{content}{project_link}\n",
        )

    def _delete_note(self, memory_id: str) -> None:
        try:
            self._note_path(memory_id).unlink()
        except FileNotFoundError:
            pass
