"""Tests for debounce manager and vault watcher."""

import time
from pathlib import Path
from devbrain.watcher.debounce import DebounceManager


def test_debounce_manager_coalescing():
    manager = DebounceManager(delay=0.1)
    call_count = 0

    def increment():
        nonlocal call_count
        call_count += 1

    # Trigger 5 rapid calls with the same key
    for _ in range(5):
        manager.debounce("test_key", increment)
        time.sleep(0.01)

    # Wait for delay to expire
    time.sleep(0.2)

    # Should only execute once
    assert call_count == 1
