"""Static Codebase Tree Generator and Entrypoint Analyzer."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

IGNORED_DIRECTORIES: Set[str] = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode",
    ".gemini",
    "target",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".turbo",
    ".output",
    "coverage",
    ".brain_data",
}

ENTRYPOINT_CANDIDATES: List[str] = [
    "server.js",
    "app.js",
    "index.js",
    "index.ts",
    "server.ts",
    "main.py",
    "app.py",
    "manage.py",
    "wsgi.py",
    "asgi.py",
    "main.go",
    "src/main.rs",
    "src/lib.rs",
]

INFRA_CANDIDATES: List[str] = [
    "docker-compose.yml",
    "docker-compose.yaml",
    "Dockerfile",
    ".env.example",
    "Makefile",
    "Procfile",
]


@dataclass
class CodebaseAnalysisResult:
    """Structure and entrypoints extracted from repository directory."""
    ascii_tree: str
    entrypoints: List[str] = field(default_factory=list)
    infra_files: List[str] = field(default_factory=list)
    subproject_dirs: List[Path] = field(default_factory=list)
    total_files: int = 0


def generate_ascii_tree(root_dir: Path, max_depth: int = 2, max_entries: int = 20) -> str:
    """Generate a clean ASCII directory tree representation."""
    root_dir = root_dir.resolve()
    lines = [f"{root_dir.name}/"]

    def _walk(current: Path, prefix: str, depth: int, count: int) -> int:
        if depth > max_depth or count >= max_entries:
            return count

        try:
            items = sorted(
                list(current.iterdir()),
                key=lambda x: (not x.is_dir(), x.name.lower()),
            )
        except Exception:
            return count

        filtered_items = [
            item for item in items
            if item.name not in IGNORED_DIRECTORIES and not item.name.startswith(".")
        ]

        for i, item in enumerate(filtered_items):
            if count >= max_entries:
                lines.append(f"{prefix}└── ... (more files truncated)")
                return count + 1

            is_last = (i == len(filtered_items) - 1)
            connector = "└── " if is_last else "├── "
            new_prefix = prefix + ("    " if is_last else "│   ")

            if item.is_dir():
                lines.append(f"{prefix}{connector}{item.name}/")
                count = _walk(item, new_prefix, depth + 1, count + 1)
            else:
                lines.append(f"{prefix}{connector}{item.name}")
                count += 1

        return count

    _walk(root_dir, "", 1, 1)
    return "\n".join(lines)


def analyze_codebase_structure(root_dir: Path) -> CodebaseAnalysisResult:
    """Analyze entrypoints, infra files, and sub-projects."""
    root_dir = root_dir.resolve()
    entrypoints = []
    infra_files = []
    subprojects = []

    # 1. Detect Entrypoints
    for candidate in ENTRYPOINT_CANDIDATES:
        f = root_dir / candidate
        if f.is_file():
            entrypoints.append(candidate)

    # 2. Detect Infra files
    for candidate in INFRA_CANDIDATES:
        f = root_dir / candidate
        if f.is_file():
            infra_files.append(candidate)

    # 3. Detect sub-projects (for container workspace detection)
    if root_dir.is_dir():
        for sub in root_dir.iterdir():
            if sub.is_dir() and sub.name not in IGNORED_DIRECTORIES and not sub.name.startswith("."):
                has_manifest = any(
                    (sub / m).is_file() for m in ["package.json", "pyproject.toml", "Cargo.toml", "go.mod", "setup.py", "requirements.txt", "Dockerfile"]
                ) or (sub / ".git").is_dir()
                if has_manifest:
                    subprojects.append(sub)

    tree = generate_ascii_tree(root_dir, max_depth=2, max_entries=25)

    return CodebaseAnalysisResult(
        ascii_tree=tree,
        entrypoints=entrypoints,
        infra_files=infra_files,
        subproject_dirs=subprojects,
    )
