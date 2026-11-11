"""Pytest configuration and environment initialization."""

import os
from pathlib import Path
import sys

import pytest

# Prevent OpenBLAS and ONNX Runtime memory arena allocation issues on Windows
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


@pytest.fixture(autouse=True)
def isolated_home(tmp_path_factory, monkeypatch):
    """Point Path.home() and home-related env vars at a throwaway directory.

    Commands such as `devbrain init` write MCP entries into IDE config files
    under the home directory; no test may touch the developer's real ones.
    """
    fake_home = tmp_path_factory.mktemp("home")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))
    monkeypatch.setenv("APPDATA", str(fake_home / "AppData" / "Roaming"))
    # Agent homes such as Hermes (%LOCALAPPDATA%\hermes) must not be found either
    monkeypatch.setenv("LOCALAPPDATA", str(fake_home / "AppData" / "Local"))
    monkeypatch.delenv("HERMES_HOME", raising=False)
    return fake_home
