"""Embedded SQLite state and relational cache for DevBrain (.brain_data/brain.db)."""

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any, Optional
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

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with foreign keys and row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

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

                CREATE TABLE IF NOT EXISTS file_cache (
                    file_path TEXT PRIMARY KEY,
                    mtime REAL NOT NULL,
                    sha256_hash TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    indexed_at TEXT NOT NULL
                );
                """
            )
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
