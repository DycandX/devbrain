"""Long-term memory: facts and preferences an agent chooses to keep across sessions.

SQLite (.brain_data/brain.db) is the record of every memory and its lifecycle.
Each active memory is mirrored as a Markdown note in 00_System/Memories/, which
makes it visible in Obsidian and searchable through the hybrid engine. Memories
that are pending, superseded, forgotten, or rejected keep their SQLite row and
have no note, so recall and briefings only ever see active ones.

Every write passes the content guard (memory/guard.py) and is recorded in the
append-only memory ledger. Pinned memories form the core memory: always shown
in briefings, within a fixed character budget.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Optional

from devbrain.core.config import BrainConfig, MemorySettings, load_config
from devbrain.core.constants import CONFIG_FILENAME, DIR_MEMORIES
from devbrain.core.fsutil import atomic_write_text
from devbrain.core.sqlite_db import BrainSQLiteStorage
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.memory.guard import MemoryRejected, guard_memory_content

MEMORY_SCOPES = ("GLOBAL", "PROJECT", "TASK", "SESSION")
MAX_MEMORY_CHARS = 1000


class CoreMemoryFull(ValueError):
    """Pinning would exceed the core memory character budget."""


class MemoryManager:
    """Write, retrieve, approve, pin, and retire memories."""

    def __init__(
        self,
        vault_path: Path,
        sqlite_storage: Optional[BrainSQLiteStorage] = None,
        engine: Optional[HybridEngine] = None,
        config: Optional[BrainConfig] = None,
    ):
        self.vault_path = Path(vault_path).resolve()
        if config is None and (self.vault_path / CONFIG_FILENAME).is_file():
            config = load_config(self.vault_path)
        self.settings: MemorySettings = config.memory if config else MemorySettings()
        self.sqlite = sqlite_storage or BrainSQLiteStorage(self.vault_path)
        self.engine = engine or HybridEngine.from_config(self.vault_path, config)
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
        pinned: bool = False,
    ) -> dict[str, Any]:
        """Store a memory. Returns {"id", "created", "status", "superseded"}.

        Raises ValueError for invalid input, MemoryRejected when the content
        guard refuses it, and CoreMemoryFull when a pin would not fit. With
        write approval on, the memory is stored as 'pending' and takes effect
        (including its pin and supersede) only once approved.
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

        try:
            guard_memory_content(content)
        except MemoryRejected as rejected:
            self.sqlite.record_memory_event("blocked", None, source, f"{rejected} | {content[:200]}")
            raise

        existing = self.sqlite.find_open_memory(content, project)
        if existing:
            return {"id": existing["id"], "created": False, "status": existing["status"], "superseded": None}

        if pinned:
            self._check_core_budget(project, len(content))

        status = "pending" if self.settings.write_approval else "active"
        memory_id = self.sqlite.upsert_memory(
            content=content,
            type=memory_type,
            scope=scope,
            project=project,
            source=source,
            status=status,
            metadata={"tags": tags or [], "supersedes": supersedes, "pin_requested": pinned},
        )
        self.sqlite.record_memory_event("created", memory_id, source, f"status={status}")

        superseded = None
        if status == "active":
            superseded = self._activate(memory_id)
        return {"id": memory_id, "created": True, "status": status, "superseded": superseded}

    def approve(self, memory_id: str) -> dict[str, Any]:
        """Activate a pending memory, applying the pin and supersede it asked for."""
        memory = self._require(memory_id)
        if memory["status"] != "pending":
            raise ValueError(f"{memory_id} is {memory['status']}, not pending.")
        if memory["metadata"].get("pin_requested"):
            self._check_core_budget(memory["project"], len(memory["content"]))
        self.sqlite.set_memory_status(memory_id, "active")
        self.sqlite.record_memory_event("approved", memory_id, "owner")
        return {"id": memory_id, "superseded": self._activate(memory_id)}

    def reject(self, memory_id: str) -> None:
        memory = self._require(memory_id)
        if memory["status"] != "pending":
            raise ValueError(f"{memory_id} is {memory['status']}, not pending.")
        self.sqlite.set_memory_status(memory_id, "rejected")
        self.sqlite.record_memory_event("rejected", memory_id, "owner")

    def patch(self, memory_id: str, old_text: str, new_text: str, source: Optional[str] = None) -> str:
        """Replace one exact span of an active memory's text. Returns the new content."""
        memory = self._require(memory_id)
        if memory["status"] != "active":
            raise ValueError(f"{memory_id} is {memory['status']}; only active memories can be edited.")
        occurrences = memory["content"].count(old_text) if old_text else 0
        if occurrences != 1:
            raise ValueError(f"The text to replace must occur exactly once; it occurs {occurrences} time(s).")

        content = " ".join(memory["content"].replace(old_text, new_text, 1).split())
        if not content or len(content) > MAX_MEMORY_CHARS:
            raise ValueError(f"The edited memory must be 1 to {MAX_MEMORY_CHARS} characters.")
        guard_memory_content(content)
        if memory.get("pinned"):
            self._check_core_budget(memory["project"], len(content) - len(memory["content"]))

        self.sqlite.update_memory_content(memory_id, content)
        self.sqlite.record_memory_event("patched", memory_id, source, f"{memory['content']} -> {content}")
        self._write_note({**memory, "content": content})
        self.engine.index_vault()
        return content

    def pin(self, memory_id: str, pinned: bool = True) -> None:
        """Add a memory to, or remove it from, the core memory shown in every briefing."""
        memory = self._require(memory_id)
        if memory["status"] != "active":
            raise ValueError(f"{memory_id} is {memory['status']}; only active memories can be pinned.")
        if pinned and not memory.get("pinned"):
            self._check_core_budget(memory["project"], len(memory["content"]))
        self.sqlite.set_memory_pinned(memory_id, pinned)
        self.sqlite.record_memory_event("pinned" if pinned else "unpinned", memory_id, "owner")

    def forget(self, memory_id: str, source: Optional[str] = None) -> bool:
        """Retire a memory. Its row is kept with status 'forgotten'; its note is removed."""
        if not self.sqlite.set_memory_status(memory_id, "forgotten"):
            return False
        self.sqlite.set_memory_pinned(memory_id, False)
        self.sqlite.record_memory_event("forgotten", memory_id, source)
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

    def core_memories(self, project: Optional[str] = None) -> list[dict[str, Any]]:
        """Pinned memories shown in every briefing: global ones plus the project's."""
        return self.sqlite.get_pinned_memories(project)

    def recall_for_briefing(self, task: str, project: str, limit: int = 5) -> list[dict[str, Any]]:
        """Memories to show when work on a project starts, besides the core memories.

        Matches for the task come first. Remaining slots go to the project's own
        most recent memories even when they do not match the task wording: they
        are few, were saved on purpose, and are the facts an agent most needs
        before touching the project. Global memories appear only on a match.
        """
        core = {m["id"] for m in self.core_memories(project)}
        found = [m for m in self.recall(f"{project} {task}", project=project, limit=limit) if m["id"] not in core]
        seen = core | {m["id"] for m in found}
        for memory in self.sqlite.get_memories(scope="PROJECT", project=project):
            if len(found) >= limit:
                break
            if memory["id"] not in seen and memory["project"] == project:
                found.append(memory)
        return found

    def list(self, status: str = "active", project: Optional[str] = None) -> list[dict[str, Any]]:
        return self.sqlite.get_memories(status=status, project=project)

    def ledger(self, memory_id: Optional[str] = None, limit: int = 50) -> list[dict[str, Any]]:
        return self.sqlite.get_memory_ledger(memory_id, limit)

    # --- Internals ---------------------------------------------------------

    def _require(self, memory_id: str) -> dict[str, Any]:
        memory = self.sqlite.get_memory(memory_id.strip().strip("`"))
        if not memory:
            raise KeyError(f"No memory with id {memory_id}.")
        return memory

    def _check_core_budget(self, project: Optional[str], extra_chars: int) -> None:
        """Refuse a pin that would push the core memory past its budget.

        Global pins and each project's pins have their own budget, the way
        Hermes keeps MEMORY.md bounded: the agent is told to make room instead
        of the oldest entry being dropped silently.
        """
        limit = self.settings.core_char_limit
        used = sum(len(m["content"]) for m in self.sqlite.get_pinned_memories(project, exact_project=True))
        if used + extra_chars > limit:
            where = f"project '{project}'" if project else "global memory"
            raise CoreMemoryFull(
                f"Core memory for {where} would use {used + extra_chars} of {limit} characters. "
                "Unpin or shorten another core memory first."
            )

    def _activate(self, memory_id: str) -> Optional[str]:
        """Make an active memory visible: note, pin, supersede, index. Returns the id it replaced."""
        memory = self._require(memory_id)
        self._write_note(memory)
        if memory["metadata"].get("pin_requested"):
            self.sqlite.set_memory_pinned(memory_id, True)

        superseded = None
        old_id = memory["metadata"].get("supersedes")
        if old_id and self.sqlite.supersede_memory(old_id, memory_id):
            self.sqlite.set_memory_pinned(old_id, False)
            self.sqlite.record_memory_event("superseded", old_id, memory["source"], f"by {memory_id}")
            self._delete_note(old_id)
            superseded = old_id

        self.engine.index_vault()
        return superseded

    # --- Markdown mirror ---------------------------------------------------

    def _note_path(self, memory_id: str) -> Path:
        return self.notes_dir / f"{memory_id}.md"

    def _write_note(self, memory: dict[str, Any]) -> None:
        scope, project, content = memory["scope"], memory["project"], memory["content"]
        tags = ["memory", scope.lower(), *memory["metadata"].get("tags", [])]
        frontmatter = [
            "---",
            f'id: "{memory["id"]}"',
            "type: memory",
            f"title: {json.dumps(content[:80], ensure_ascii=False)}",
            f'created: "{memory.get("created_at") or datetime.now(timezone.utc).isoformat()}"',
            f"memory_type: {json.dumps(memory['type'])}",
            f"scope: {scope}",
        ]
        if project:
            frontmatter.append(f"project: {json.dumps(project, ensure_ascii=False)}")
        frontmatter += [f"tags: {json.dumps(tags, ensure_ascii=False)}", "---", ""]

        project_link = f"\n\nProject: [[{project}]]" if project else ""
        atomic_write_text(
            self._note_path(memory["id"]),
            "\n".join(frontmatter) + f"# Memory {memory['id']}\n\n{content}{project_link}\n",
        )

    def _delete_note(self, memory_id: str) -> None:
        try:
            self._note_path(memory_id).unlink()
        except FileNotFoundError:
            pass
