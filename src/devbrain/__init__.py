"""devbrain: Central AI Second Brain Hub for Multi-Agent Coding and Obsidian."""

import os
import sys

# Optimize OpenBLAS and ONNX threads on Windows
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

__version__ = "1.1.0-alpha"
