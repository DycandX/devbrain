"""Ingestion Orchestrator Service managing session harvesting and deduplication."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict, List, Optional

from devbrain.core.config import BrainConfig
from devbrain.core.constants import BRAIN_DATA_DIR, DIR_INBOX
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.harvester.discovery import discover_sessions
from devbrain.harvester.extractor import extract_session_payload
from devbrain.harvester.formatter import format_session_note

INGESTED_REGISTRY_FILE = "ingested_sessions.json"


@dataclass
class IngestionResult:
    """Summary metrics of an ingestion run."""
    discovered: int
    ingested: int
    skipped: int
    total_redactions: int
    created_files: List[Path]


class IngestionService:
    """Orchestrator for discovering, sanitizing, and seeding AI agent sessions into Obsidian."""

    def __init__(self, vault_path: Path, config: Optional[BrainConfig] = None):
        self.vault_path = vault_path.resolve()
        self.config = config or BrainConfig(vault_path=str(self.vault_path))
        self.data_dir = self.vault_path / BRAIN_DATA_DIR
        self.registry_file = self.data_dir / INGESTED_REGISTRY_FILE
        self.inbox_dir = self.vault_path / DIR_INBOX

        self._ingested_ids = self._load_registry()

    def _load_registry(self) -> Dict[str, str]:
        """Load history of previously ingested session IDs."""
        if not self.registry_file.is_file():
            return {}
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_registry(self):
        """Save ingested session registry to .brain_data/."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(self._ingested_ids, f, indent=2)
        except Exception:
            pass

    def run_ingestion(
        self,
        sources: Optional[List[str]] = None,
        limit: Optional[int] = None,
        dry_run: bool = False,
        custom_paths: Optional[Dict[str, Path]] = None,
    ) -> IngestionResult:
        """Execute full ingestion pipeline."""
        discovered = discover_sessions(sources=sources, custom_paths=custom_paths)
        if limit and limit > 0:
            discovered = discovered[:limit]

        ingested_count = 0
        skipped_count = 0
        total_redactions = 0
        created_files: List[Path] = []

        for session in discovered:
            # Deduplication check
            unique_key = f"{session.source_name}:{session.session_id}"
            if unique_key in self._ingested_ids and not dry_run:
                skipped_count += 1
                continue

            # Extract payload
            payload = extract_session_payload(session)
            if not payload:
                skipped_count += 1
                continue

            total_redactions += payload.num_redactions

            if dry_run:
                ingested_count += 1
                continue

            # Format and write to 90_Agent_Inbox/<source>/
            target_folder = self.inbox_dir / session.source_name
            target_folder.mkdir(parents=True, exist_ok=True)

            filename, content = format_session_note(payload, device_name=self.config.device_name)
            target_file = target_folder / filename

            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)

            self._ingested_ids[unique_key] = target_file.name
            created_files.append(target_file)
            ingested_count += 1

        if not dry_run:
            self._save_registry()
            # Trigger incremental vault indexing if new files were created
            if created_files:
                try:
                    engine = HybridEngine(vault_path=self.vault_path)
                    engine.initialize()
                    engine.index_vault(force_reindex=False)
                except Exception:
                    pass

        return IngestionResult(
            discovered=len(discovered),
            ingested=ingested_count,
            skipped=skipped_count,
            total_redactions=total_redactions,
            created_files=created_files,
        )
