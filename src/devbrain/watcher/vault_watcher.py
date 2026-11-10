"""Real-time file system watcher for incremental vault re-indexing."""

from pathlib import Path
from typing import Callable, Optional
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from devbrain.engine.hybrid_search import HybridEngine
from devbrain.watcher.debounce import DebounceManager


class VaultEventHandler(FileSystemEventHandler):
    """Handles created, modified, deleted events on Markdown notes in vault."""

    def __init__(
        self,
        engine: HybridEngine,
        debounce_manager: DebounceManager,
        on_change: Optional[Callable[[str, str], None]] = None,
    ):
        super().__init__()
        self.engine = engine
        self.debounce = debounce_manager
        self.on_change = on_change

    def _should_process(self, path_str: str) -> bool:
        path = Path(path_str)
        if path.suffix.lower() != ".md" or path.is_dir():
            return False
        return not self.engine.is_ignored(path, self.engine.vault_path)

    def on_created(self, event: FileSystemEvent):
        if self._should_process(event.src_path):
            self.debounce.debounce(
                event.src_path,
                lambda: self._handle_event("created", event.src_path),
            )

    def on_modified(self, event: FileSystemEvent):
        if self._should_process(event.src_path):
            self.debounce.debounce(
                event.src_path,
                lambda: self._handle_event("modified", event.src_path),
            )

    def on_deleted(self, event: FileSystemEvent):
        if self._should_process(event.src_path):
            self.debounce.debounce(
                event.src_path,
                lambda: self._handle_event("deleted", event.src_path),
            )

    def _handle_event(self, event_type: str, src_path: str):
        # Runs on a timer thread: a failed re-index must not kill the watcher.
        try:
            self.engine.index_vault(force_reindex=False)
        except Exception:
            return
        if self.on_change:
            self.on_change(event_type, src_path)


class VaultWatcher:
    """Service to watch vault directory in background and trigger indexing."""

    def __init__(
        self,
        engine: HybridEngine,
        on_change: Optional[Callable[[str, str], None]] = None,
    ):
        self.engine = engine
        self.debounce = DebounceManager(delay=0.5)
        self.handler = VaultEventHandler(self.engine, self.debounce, on_change=on_change)
        self.observer = Observer()

    def start(self):
        """Start the background filesystem observer."""
        self.observer.schedule(self.handler, str(self.engine.vault_path), recursive=True)
        self.observer.start()

    def stop(self):
        """Stop the background filesystem observer."""
        self.debounce.cancel_all()
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=2.0)
