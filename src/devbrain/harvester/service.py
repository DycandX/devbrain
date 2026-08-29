"""Ingestion Orchestrator Service managing session harvesting, project seeding, and entity linking."""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from devbrain.core.config import BrainConfig
from devbrain.core.constants import BRAIN_DATA_DIR, DIR_INBOX, DIR_PROJECTS
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.harvester.discovery import discover_sessions
from devbrain.harvester.entity_linker import inject_backlink_to_project, match_session_to_project
from devbrain.harvester.extractor import extract_session_payload
from devbrain.harvester.formatter import format_session_note
from devbrain.harvester.inspector import RepoType
from devbrain.harvester.project_harvester import (
    ScannedProjectMetadata,
    scan_project_metadata,
    seed_project_to_vault,
)

INGESTED_REGISTRY_FILE = "ingested_sessions.json"


@dataclass
class IngestionResult:
    """Summary metrics of an ingestion run."""
    discovered: int
    ingested: int
    skipped: int
    total_redactions: int
    created_files: List[Path] = field(default_factory=list)
    linked_projects: int = 0


class IngestionService:
    """Orchestrator for discovering, sanitizing, linking, and seeding AI agent sessions & repositories."""

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

    def ingest_single_project(
        self,
        repo_path: Path,
        explicit_type: Optional[str] = None,
        dry_run: bool = False,
    ) -> Tuple[ScannedProjectMetadata, Union[Optional[Path], List[Tuple[ScannedProjectMetadata, Optional[Path]]]]]:
        """Scan and seed a single repository, or auto-delegate if it's a multi-project container."""
        # Self-Ingestion Guard
        if repo_path.resolve() == self.vault_path.resolve():
            meta = scan_project_metadata(repo_path, explicit_type=explicit_type)
            return meta, None

        metadata = scan_project_metadata(repo_path, explicit_type=explicit_type)
        
        # Auto-delegation for container workspace folders (e.g. _fxmedia)
        if metadata.repo_type == RepoType.CONTAINER:
            sub_results = self.ingest_workspace_projects(root_dirs=[repo_path], dry_run=dry_run)
            return metadata, sub_results

        created_file = None
        if not dry_run:
            created_file = seed_project_to_vault(metadata, vault_path=self.vault_path)
        return metadata, created_file

    def ingest_workspace_projects(
        self,
        root_dirs: Optional[List[Path]] = None,
        dry_run: bool = False,
    ) -> List[Tuple[ScannedProjectMetadata, Optional[Path]]]:
        """Batch scan workspace root folders for Git repositories and codebases with Self-Ingestion Guard."""
        roots = root_dirs or [Path(p) for p in self.config.workspace_roots if Path(p).is_dir()]
        if not roots:
            # Fallback: parent of vault path or current cwd
            roots = [self.vault_path.parent]

        results = []
        visited_dirs = set()

        for root in roots:
            if not root.is_dir():
                continue
            for item in root.iterdir():
                if not item.is_dir() or item.name.startswith("."):
                    continue
                if item.resolve() in visited_dirs:
                    continue
                # Self-Ingestion Guard: Skip if item is the Central Brain vault itself
                if item.resolve() == self.vault_path.resolve():
                    continue

                visited_dirs.add(item.resolve())

                # Check if it has a git directory or a known code manifest
                has_git = (item / ".git").is_dir()
                has_manifest = any((item / m).is_file() for m in ["pyproject.toml", "package.json", "Cargo.toml", "go.mod", "setup.py", "requirements.txt", "SKILL.md", "Dockerfile"])
                
                if has_git or has_manifest:
                    meta, path = self.ingest_single_project(item, dry_run=dry_run)
                    if isinstance(path, list):
                        results.extend(path)
                    elif path is not None:
                        results.append((meta, path))

        return results

    def run_ingestion(
        self,
        sources: Optional[List[str]] = None,
        limit: Optional[int] = None,
        dry_run: bool = False,
        custom_paths: Optional[Dict[str, Path]] = None,
    ) -> IngestionResult:
        """Execute full AI agent session ingestion pipeline with auto-entity linking."""
        discovered = discover_sessions(sources=sources, custom_paths=custom_paths)
        if limit and limit > 0:
            discovered = discovered[:limit]

        ingested_count = 0
        skipped_count = 0
        total_redactions = 0
        linked_projects = 0
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

            # Match or auto-provision project node
            matched_project = match_session_to_project(payload.workspace_hint, self.vault_path)
            
            # Auto-provision project card if workspace exists on disk but not in vault
            if not matched_project and payload.workspace_hint:
                hint_path = Path(payload.workspace_hint)
                if hint_path.is_dir() and hint_path.resolve() != self.vault_path.resolve():
                    try:
                        p_meta, p_file = self.ingest_single_project(hint_path, dry_run=False)
                        if isinstance(p_file, Path):
                            matched_project = (p_meta.name, f"10_Projects/{p_meta.clean_name}/README")
                    except Exception:
                        pass

            if matched_project:
                linked_projects += 1

            # Format and write to 90_Agent_Inbox/<source>/
            target_folder = self.inbox_dir / session.source_name
            target_folder.mkdir(parents=True, exist_ok=True)

            filename, content = format_session_note(
                payload,
                device_name=self.config.device_name,
                matched_project=matched_project,
            )
            target_file = target_folder / filename

            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)

            # Bidirectional backlink injection
            if matched_project:
                try:
                    _, proj_rel = matched_project
                    proj_readme = self.vault_path / f"{proj_rel}.md"
                    rel_session = f"90_Agent_Inbox/{session.source_name}/{filename}"
                    date_str = payload.created_time.strftime("%Y-%m-%d")
                    inject_backlink_to_project(
                        project_readme=proj_readme,
                        session_title=payload.title,
                        session_rel_path=rel_session,
                        created_date=date_str,
                    )
                except Exception:
                    pass

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
            linked_projects=linked_projects,
        )
