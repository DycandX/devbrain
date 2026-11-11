"""Embedded SQLite state and relational cache for DevBrain (.brain_data/brain.db)."""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator, Optional
import uuid

from devbrain.core.constants import BRAIN_DATA_DIR


class BrainSQLiteStorage:
    """Manages the embedded SQLite cache for relational queries, memory scopes, and ADRs."""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path).resolve()
        self.db_dir = self.vault_path / BRAIN_DATA_DIR
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_dir / "brain.db"
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Yield a configured SQLite connection, committing on success and always closing it.

        sqlite3's own context manager only ends the transaction; without the
        explicit close the file handle stays open, which on Windows keeps
        brain.db locked.
        """
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            with conn:
                yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initializes database schema if tables do not exist."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    scope TEXT NOT NULL DEFAULT 'GLOBAL',
                    project TEXT,
                    confidence REAL NOT NULL DEFAULT 1.0,
                    source TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    superseded_by TEXT,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_memories_scope ON memories(scope);
                CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project);
                CREATE INDEX IF NOT EXISTS idx_memories_status ON memories(status);
                CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);

                CREATE TABLE IF NOT EXISTS decisions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    project TEXT,
                    status TEXT NOT NULL DEFAULT 'accepted',
                    file_path TEXT NOT NULL,
                    date TEXT NOT NULL,
                    summary TEXT,
                    superseded_by TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(project);
                CREATE INDEX IF NOT EXISTS idx_decisions_status ON decisions(status);

                CREATE TABLE IF NOT EXISTS memory_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id TEXT,
                    action TEXT NOT NULL,
                    source TEXT,
                    detail TEXT,
                    at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_memory_ledger_memory ON memory_ledger(memory_id);

                CREATE TABLE IF NOT EXISTS file_cache (
                    file_path TEXT PRIMARY KEY,
                    mtime REAL NOT NULL,
                    sha256_hash TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    indexed_at TEXT NOT NULL
                );
                """
            )
            # Columns added after the first release of the schema
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(memories)")}
            if "pinned" not in columns:
                conn.execute("ALTER TABLE memories ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0")
            conn.commit()

    # --- Memory Operations ---

    def upsert_memory(
        self,
        content: str,
        type: str = "fact",
        scope: str = "GLOBAL",
        project: Optional[str] = None,
        confidence: float = 1.0,
        source: Optional[str] = None,
        status: str = "active",
        memory_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Insert or update a memory record."""
        mid = memory_id or f"mem_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()
        meta_str = json.dumps(metadata or {}, ensure_ascii=False)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO memories (
                    id, type, content, scope, project, confidence,
                    source, status, metadata_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    type=excluded.type,
                    content=excluded.content,
                    scope=excluded.scope,
                    project=excluded.project,
                    confidence=excluded.confidence,
                    source=excluded.source,
                    status=excluded.status,
                    metadata_json=excluded.metadata_json,
                    updated_at=excluded.updated_at;
                """,
                (
                    mid,
                    type,
                    content,
                    scope.upper(),
                    project,
                    confidence,
                    source,
                    status,
                    meta_str,
                    now,
                    now,
                ),
            )
            conn.commit()
        return mid

    def get_memories(
        self,
        scope: Optional[str] = None,
        project: Optional[str] = None,
        status: str = "active",
        type: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Retrieve memories matching filters."""
        query = "SELECT * FROM memories WHERE status = ?"
        params: list[Any] = [status]

        if scope:
            query += " AND scope = ?"
            params.append(scope.upper())
        if project:
            query += " AND (project = ? OR project IS NULL)"
            params.append(project)
        if type:
            query += " AND type = ?"
            params.append(type)

        query += " ORDER BY updated_at DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            results = []
            for row in rows:
                item = dict(row)
                item["metadata"] = json.loads(item["metadata_json"] or "{}")
                results.append(item)
            return results

    def get_memory(self, memory_id: str) -> Optional[dict[str, Any]]:
        """Retrieve one memory by id, whatever its status."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
        if not row:
            return None
        item = dict(row)
        item["metadata"] = json.loads(item["metadata_json"] or "{}")
        return item

    def find_active_memory(self, content: str, project: Optional[str] = None) -> Optional[dict[str, Any]]:
        """Find an active memory with exactly this content in the same project."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM memories WHERE status = 'active' AND content = ? AND project IS ?",
                (content, project),
            ).fetchone()
        return dict(row) if row else None

    def set_memory_status(self, memory_id: str, status: str) -> bool:
        """Change the lifecycle status of a memory (e.g. 'forgotten')."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cur = conn.execute(
                "UPDATE memories SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, memory_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def find_open_memory(self, content: str, project: Optional[str] = None) -> Optional[dict[str, Any]]:
        """Find an active or pending memory with exactly this content in the same project."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM memories WHERE status IN ('active', 'pending') AND content = ? AND project IS ?",
                (content, project),
            ).fetchone()
        return dict(row) if row else None

    def update_memory_content(self, memory_id: str, content: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cur = conn.execute(
                "UPDATE memories SET content = ?, updated_at = ? WHERE id = ?", (content, now, memory_id)
            )
            return cur.rowcount > 0

    def set_memory_pinned(self, memory_id: str, pinned: bool) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cur = conn.execute(
                "UPDATE memories SET pinned = ?, updated_at = ? WHERE id = ?", (int(pinned), now, memory_id)
            )
            return cur.rowcount > 0

    def get_pinned_memories(self, project: Optional[str] = None, exact_project: bool = False) -> list[dict[str, Any]]:
        """Active pinned memories: global ones plus the project's, or only the project's."""
        query = "SELECT * FROM memories WHERE status = 'active' AND pinned = 1"
        params: list[Any] = []
        if exact_project:
            query += " AND project IS ?"
            params.append(project)
        elif project:
            query += " AND (project = ? OR project IS NULL)"
            params.append(project)
        else:
            query += " AND project IS NULL"
        query += " ORDER BY created_at ASC"
        with self._get_connection() as conn:
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def record_memory_event(
        self, action: str, memory_id: Optional[str] = None, source: Optional[str] = None, detail: str = ""
    ) -> None:
        """Append an entry to the memory ledger. Entries are never updated or deleted."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO memory_ledger (memory_id, action, source, detail, at) VALUES (?, ?, ?, ?, ?)",
                (memory_id, action, source, detail, now),
            )

    def get_memory_ledger(self, memory_id: Optional[str] = None, limit: int = 50) -> list[dict[str, Any]]:
        query = "SELECT * FROM memory_ledger"
        params: list[Any] = []
        if memory_id:
            query += " WHERE memory_id = ?"
            params.append(memory_id)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self._get_connection() as conn:
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def supersede_memory(self, old_memory_id: str, new_memory_id: str) -> bool:
        """Mark an old memory as superseded by a newer memory."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                UPDATE memories
                SET status = 'superseded', superseded_by = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_memory_id, now, old_memory_id),
            )
            conn.commit()
            return cur.rowcount > 0

    # --- Decision (ADR) Operations ---

    def upsert_decision(
        self,
        id: str,
        title: str,
        file_path: str,
        date: str,
        project: Optional[str] = None,
        status: str = "accepted",
        summary: Optional[str] = None,
        superseded_by: Optional[str] = None,
    ) -> str:
        """Insert or update an Architecture Decision Record."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO decisions (
                    id, title, project, status, file_path,
                    date, summary, superseded_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    project=excluded.project,
                    status=excluded.status,
                    file_path=excluded.file_path,
                    date=excluded.date,
                    summary=excluded.summary,
                    superseded_by=excluded.superseded_by,
                    updated_at=excluded.updated_at;
                """,
                (
                    id,
                    title,
                    project,
                    status,
                    file_path,
                    date,
                    summary,
                    superseded_by,
                    now,
                    now,
                ),
            )
            conn.commit()
        return id

    def get_decisions(
        self,
        project: Optional[str] = None,
        status: Optional[str] = "accepted",
    ) -> list[dict[str, Any]]:
        """Retrieve decisions matching project and status filters."""
        query = "SELECT * FROM decisions WHERE 1=1"
        params: list[Any] = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if project:
            query += " AND (project = ? OR project IS NULL)"
            params.append(project)

        query += " ORDER BY id ASC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    # --- File Cache Operations ---

    def update_file_cache(
        self,
        file_path: str,
        mtime: float,
        sha256_hash: str,
        chunk_count: int = 0,
    ) -> None:
        """Update file cache record."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO file_cache (file_path, mtime, sha256_hash, chunk_count, indexed_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    mtime=excluded.mtime,
                    sha256_hash=excluded.sha256_hash,
                    chunk_count=excluded.chunk_count,
                    indexed_at=excluded.indexed_at;
                """,
                (file_path, mtime, sha256_hash, chunk_count, now),
            )
            conn.commit()

    def get_file_cache(self, file_path: str) -> Optional[dict[str, Any]]:
        """Retrieve cached mtime and hash for a file."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM file_cache WHERE file_path = ?", (file_path,)
            ).fetchone()
            return dict(row) if row else None
