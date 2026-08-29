"""Central AI Second Brain Hub (devbrain).

A single source of truth for multi-agent coding workflows,
Obsidian integration, hybrid semantic memory, and graph connectivity.
"""

import os

# Limit OpenBLAS / OMP threads on startup to prevent Windows memory retry loops on Python 3.14
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

__version__ = "1.2.0-alpha"
__author__ = "Central AI Brain Team"
