"""Debounce mechanism for coalescing rapid filesystem write events."""

import threading
from typing import Callable, Dict


class DebounceManager:
    """Debounce timer queue grouping rapid file modifications (e.g. live typing)."""

    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self._timers: Dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def debounce(self, key: str, action: Callable[[], None]):
        """Schedule an action to run after delay, resetting timer if called again."""
        with self._lock:
            if key in self._timers:
                self._timers[key].cancel()

            timer = threading.Timer(self.delay, self._execute_and_cleanup, args=[key, action])
            self._timers[key] = timer
            timer.daemon = True
            timer.start()

    def _execute_and_cleanup(self, key: str, action: Callable[[], None]):
        with self._lock:
            self._timers.pop(key, None)
        action()

    def cancel_all(self):
        """Cancel all pending debounce timers."""
        with self._lock:
            for timer in self._timers.values():
                timer.cancel()
            self._timers.clear()
