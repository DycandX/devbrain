"""Shared rules for telling project folders, vaults, and container folders apart."""

from pathlib import Path
import re
from typing import List

from devbrain.core.constants import CONFIG_FILENAME

# A file with one of these names at a folder's top level makes it a project.
PROJECT_MANIFESTS = (
    "pyproject.toml",
    "setup.py",
    "requirements.txt",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pubspec.yaml",
    "composer.json",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "CMakeLists.txt",
    "Makefile",
    "Dockerfile",
)
PROJECT_MANIFEST_GLOBS = ("*.csproj", "*.sln")

# Folders never descended into while looking for projects.
SKIPPED_DIR_NAMES = {
    "node_modules", "venv", ".venv", "env", "vendor", "build", "dist", "target", "__pycache__",
}

# How many folder levels below a workspace root are searched for projects.
MAX_SCAN_DEPTH = 3

_SANDBOX_WORDS = {"test", "tests", "testing", "sandbox", "playground", "scratch", "tmp", "temp"}

# Names that scaffolding tools put in a manifest and nobody renames. They say
# nothing about the project, so the folder name is used instead.
GENERIC_PROJECT_NAMES = {
    "laravel", "app", "my-app", "myapp", "project", "example", "starter", "template",
    "vite-project", "next-app", "react-app", "flutter_application_1", "temp-app", "untitled",
}


def has_project_marker(path: Path) -> bool:
    """True when the folder itself is a codebase: a git repository or a known manifest."""
    if (path / ".git").is_dir():
        return True
    if any((path / name).is_file() for name in PROJECT_MANIFESTS):
        return True
    return any(next(path.glob(pattern), None) is not None for pattern in PROJECT_MANIFEST_GLOBS)


def is_obsidian_vault(path: Path) -> bool:
    """True for a devbrain vault, or an Obsidian vault that is not also a codebase.

    A project that merely keeps its notes in Obsidian (.obsidian next to a
    manifest) still counts as a project.
    """
    if (path / CONFIG_FILENAME).is_file():
        return True
    return (path / ".obsidian").is_dir() and not has_project_marker(path)


def is_scannable_dir(path: Path) -> bool:
    """A folder worth looking into while searching for projects."""
    return path.is_dir() and not path.name.startswith(".") and path.name not in SKIPPED_DIR_NAMES


def find_subprojects(path: Path, max_depth: int = MAX_SCAN_DEPTH) -> List[Path]:
    """Project folders nested under a folder that is not itself a project."""
    found: List[Path] = []
    if max_depth <= 0:
        return found
    try:
        children = sorted(p for p in path.iterdir() if is_scannable_dir(p))
    except OSError:
        return found

    for child in children:
        if is_obsidian_vault(child):
            continue
        if has_project_marker(child):
            found.append(child)
        else:
            found.extend(find_subprojects(child, max_depth - 1))
    return found


def looks_like_sandbox(folder_name: str) -> bool:
    """Guess from its name whether a group folder holds throwaway experiments.

    The first word decides: '_TEST' and 'test readme' are sandboxes,
    'flowkit-test-suite' is not.
    """
    words = re.split(r"[^a-z0-9]+", folder_name.lower().strip("_- "))
    return bool(words) and words[0] in _SANDBOX_WORDS


def slugify(name: str) -> str:
    """Lowercase tag-safe form of a folder name: '_fxmedia' -> 'fxmedia'."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
