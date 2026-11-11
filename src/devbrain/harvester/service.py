"""Ingestion Orchestrator Service managing session harvesting, project seeding, and entity linking."""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from devbrain.core.config import BrainConfig
from devbrain.core.constants import BRAIN_DATA_DIR, DIR_INBOX, DIR_PROJECTS, DIR_SYSTEM
from devbrain.core.fsutil import atomic_write_json, atomic_write_text
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.engine.parser import parse_frontmatter
from devbrain.harvester.discovery import discover_sessions
from devbrain.harvester.entity_linker import inject_backlink_to_project, match_session_to_project
from devbrain.harvester.extractor import extract_session_payload
from devbrain.harvester.formatter import format_session_note
from devbrain.harvester.inspector import RepoType, inspect_repository_type
from devbrain.harvester.markers import (
    MAX_SCAN_DEPTH,
    find_subprojects,
    has_project_marker,
    is_obsidian_vault,
    is_scannable_dir,
    looks_like_sandbox,
    slugify,
)
from devbrain.harvester.project_harvester import (
    ScannedProjectMetadata,
    scan_project_metadata,
    seed_project_to_vault,
)

INGESTED_REGISTRY_FILE = "ingested_sessions.json"

# Registry value per ingested session. Entries written before v1.7 are a bare
# note filename; newer ones also record the transcript mtime.
RegistryEntry = Union[str, Dict[str, Union[str, float]]]


def _registry_filename(entry: RegistryEntry) -> str:
    return entry if isinstance(entry, str) else str(entry["file"])


def _session_changed(entry: RegistryEntry, last_modified: float) -> bool:
    """True when the session was modified after it was last ingested."""
    if isinstance(entry, str):
        return False
    return last_modified > float(entry.get("mtime", 0.0))


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
        # Card name -> project path claimed while scanning; a dry run writes no
        # cards, so name clashes within one run are tracked here.
        self._claimed_cards: Dict[str, str] = {}

    def _load_registry(self) -> Dict[str, RegistryEntry]:
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
        try:
            atomic_write_json(self.registry_file, self._ingested_ids)
        except OSError:
            pass

    def ingest_single_project(
        self,
        repo_path: Path,
        explicit_type: Optional[str] = None,
        dry_run: bool = False,
    ) -> Tuple[ScannedProjectMetadata, Union[Optional[Path], List[Tuple[ScannedProjectMetadata, Optional[Path]]]]]:
        """Scan and seed a single repository, or auto-delegate if it's a multi-project container."""
        repo_path = repo_path.resolve()
        metadata = scan_project_metadata(repo_path, explicit_type=explicit_type)

        # Self-Ingestion Guard
        if repo_path == self.vault_path.resolve():
            return metadata, None

        # Auto-delegation for container workspace folders (e.g. _fxmedia)
        if metadata.repo_type == RepoType.CONTAINER:
            results: List[Tuple[ScannedProjectMetadata, Optional[Path]]] = []
            self._scan_directory(repo_path, repo_path.name, MAX_SCAN_DEPTH, dry_run, results, set())
            return metadata, results

        self._apply_group(metadata, self._infer_group(repo_path))
        return metadata, self._seed(metadata, dry_run)

    def ingest_workspace_projects(
        self,
        root_dirs: Optional[List[Path]] = None,
        dry_run: bool = False,
    ) -> List[Tuple[ScannedProjectMetadata, Optional[Path]]]:
        """Batch scan workspace roots for projects, descending into multi-project folders.

        A folder that is not a project but holds projects (up to MAX_SCAN_DEPTH
        levels down) becomes their group. Vaults are skipped.
        """
        roots = root_dirs or [Path(p) for p in self.config.workspace_roots if Path(p).is_dir()]
        if not roots:
            # Fallback: parent of vault path or current cwd
            roots = [self.vault_path.parent]

        results: List[Tuple[ScannedProjectMetadata, Optional[Path]]] = []
        visited: set = set()
        for root in roots:
            if root.is_dir():
                self._scan_directory(root, None, MAX_SCAN_DEPTH, dry_run, results, visited)
        return results

    # --- Scanning internals ------------------------------------------------

    def _scan_directory(
        self,
        directory: Path,
        group: Optional[str],
        depth: int,
        dry_run: bool,
        results: List[Tuple[ScannedProjectMetadata, Optional[Path]]],
        visited: set,
    ) -> None:
        """Seed every project directly under `directory`, recursing into multi-project folders."""
        try:
            children = sorted(p for p in directory.iterdir() if is_scannable_dir(p))
        except OSError:
            return

        # Projects sitting directly in this folder go first, so on a name clash they
        # keep the plain card name and the nested one gets the group prefix
        children.sort(key=lambda p: not has_project_marker(p))

        vault = self.vault_path.resolve()
        for item in children:
            resolved = item.resolve()
            if resolved in visited or resolved == vault or is_obsidian_vault(item):
                continue
            visited.add(resolved)

            if has_project_marker(item) or (item / "SKILL.md").is_file():
                metadata = scan_project_metadata(item)
                if metadata.repo_type in (RepoType.CONTAINER, RepoType.UNKNOWN):
                    continue
                self._apply_group(metadata, group)
                results.append((metadata, self._seed(metadata, dry_run)))
            elif depth > 1 and (nested := find_subprojects(item, depth - 1)):
                # The outermost multi-project folder names the group. A folder that
                # merely wraps one project does not, unless it is configured as one.
                is_group = (
                    len(nested) > 1
                    or item.name in self.config.project_groups
                    or looks_like_sandbox(item.name)
                )
                next_group = group or (item.name if is_group else None)
                self._scan_directory(item, next_group, depth - 1, dry_run, results, visited)
            elif group is not None:
                # Inside a group, a folder of documents is worth recording too
                repo_type, _ = inspect_repository_type(item)
                if repo_type == RepoType.KNOWLEDGE:
                    metadata = scan_project_metadata(item)
                    self._apply_group(metadata, group)
                    results.append((metadata, self._seed(metadata, dry_run)))

    def _infer_group(self, repo_path: Path) -> Optional[str]:
        """Group of a project scanned on its own: its parent folder, when that is a known group."""
        parent = repo_path.parent
        if parent.name in self.config.project_groups:
            return parent.name
        roots = {Path(p).resolve() for p in self.config.workspace_roots}
        if parent.parent.resolve() in roots and not has_project_marker(parent):
            return parent.name
        return None

    def _apply_group(self, metadata: ScannedProjectMetadata, group: Optional[str]) -> None:
        """Record which group a project belongs to, using per-group settings when configured."""
        if not group:
            return
        settings = self.config.project_groups.get(group)
        metadata.group = group
        metadata.group_label = (settings.label if settings and settings.label else None) or group.strip("_- ") or group
        metadata.sandbox = (
            settings.sandbox if settings and settings.sandbox is not None else looks_like_sandbox(group)
        )

    def _seed(self, metadata: ScannedProjectMetadata, dry_run: bool) -> Optional[Path]:
        if metadata.repo_type == RepoType.PROJECT:
            metadata.clean_name = self._unique_card_name(metadata)
        if dry_run:
            return None
        return seed_project_to_vault(metadata, vault_path=self.vault_path)

    def _unique_card_name(self, metadata: ScannedProjectMetadata) -> str:
        """Card folder name for a project, prefixed when another project already owns it."""
        name = metadata.clean_name
        own_path = str(metadata.repo_path).replace("\\", "/").lower()
        parent = slugify(metadata.repo_path.parent.name)
        group = slugify(metadata.group) if metadata.group else parent

        candidates = [name, f"{group}-{name}", f"{group}-{parent}-{name}"]
        candidates += [f"{group}-{name}-{n}" for n in range(2, 50)]
        for candidate in candidates:
            if self._card_owner(candidate) in (None, own_path):
                self._claimed_cards[candidate.lower()] = own_path
                return candidate
        return candidates[-1]

    def _card_owner(self, card_name: str) -> Optional[str]:
        """Project path that holds a card name, from this run or from the vault."""
        claimed = self._claimed_cards.get(card_name.lower())
        if claimed:
            return claimed
        card = self.vault_path / DIR_PROJECTS / card_name / "README.md"
        if not card.is_file():
            return None
        meta, _ = parse_frontmatter(card.read_text(encoding="utf-8", errors="replace"))
        return str(meta.get("local_path", "")).lower() or "unknown"

    def _mirror_hermes_memory(self, custom_paths: Optional[Dict[str, Path]]) -> Optional[Path]:
        """Copy Hermes' core memory into one vault note when it changed. Returns the note if written."""
        from datetime import datetime, timezone

        from devbrain.harvester.hermes import read_core_memory, render_core_memory_note
        from devbrain.integrations.hermes import hermes_home

        home = Path(custom_paths["hermes"]) if custom_paths and "hermes" in custom_paths else hermes_home()
        if home is None or not (home / "memories").is_dir():
            return None
        memory = read_core_memory(home)
        target = self.vault_path / DIR_SYSTEM / "Hermes_Memory.md"
        previous = target.read_text(encoding="utf-8") if target.is_file() else ""
        now = datetime.now(timezone.utc).isoformat()
        content = render_core_memory_note(memory, home, now)
        # Compare without the timestamps so an unchanged memory is not rewritten
        strip = lambda t: "\n".join(l for l in t.splitlines() if not l.startswith(("created:", "updated:")))  # noqa: E731
        if strip(previous) == strip(content):
            return None
        if previous:
            old_created = next((l for l in previous.splitlines() if l.startswith("created:")), None)
            if old_created:
                content = content.replace(f"created: {json.dumps(now)}", old_created, 1)
        atomic_write_text(target, content)
        return target

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
            # Deduplication check: skip unless the session changed since it was ingested
            unique_key = f"{session.source_name}:{session.session_id}"
            previous = self._ingested_ids.get(unique_key)
            if previous is not None and not dry_run and not _session_changed(previous, session.last_modified):
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
            
            # Auto-provision a project card when the session ran in a project folder
            # that has no card yet. Only the folder itself is scanned: a session that
            # ran in a parent folder (the home directory, a workspace root) must not
            # trigger a scan of everything below it.
            if not matched_project and payload.workspace_hint:
                hint_path = Path(payload.workspace_hint)
                if (
                    hint_path.is_dir()
                    and has_project_marker(hint_path)
                    and hint_path.resolve() not in (self.vault_path.resolve(), Path.home().resolve())
                ):
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
            # A re-ingested session overwrites its existing note instead of adding a new one
            if previous is not None:
                filename = _registry_filename(previous)
            target_file = target_folder / filename

            atomic_write_text(target_file, content)

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

            self._ingested_ids[unique_key] = {"file": target_file.name, "mtime": session.last_modified}
            created_files.append(target_file)
            ingested_count += 1

        if not dry_run and (not sources or "hermes" in sources):
            note = self._mirror_hermes_memory(custom_paths)
            if note:
                created_files.append(note)

        if not dry_run:
            self._save_registry()
            # Trigger incremental vault indexing if new files were created
            if created_files:
                try:
                    engine = HybridEngine.from_config(self.vault_path, self.config)
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
