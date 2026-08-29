"""Multi-Language Dependency and Manifest Parser."""

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import List, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


@dataclass
class ParsedManifest:
    """Standardized metadata extracted from repository manifest files."""
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    stack_tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


def parse_python_manifest(repo_path: Path) -> ParsedManifest:
    """Parse pyproject.toml, setup.py, or requirements.txt."""
    manifest = ParsedManifest(languages=["Python"])
    pyproject_file = repo_path / "pyproject.toml"
    req_file = repo_path / "requirements.txt"

    if pyproject_file.is_file():
        try:
            with open(pyproject_file, "rb") as f:
                data = tomllib.load(f)

            proj = data.get("project", {})
            manifest.name = proj.get("name") or data.get("tool", {}).get("poetry", {}).get("name")
            manifest.version = proj.get("version") or data.get("tool", {}).get("poetry", {}).get("version")
            manifest.description = proj.get("description") or data.get("tool", {}).get("poetry", {}).get("description")

            deps = []
            if "dependencies" in proj and isinstance(proj["dependencies"], list):
                for d in proj["dependencies"]:
                    dep_name = re.split(r"[><=~!;]", d)[0].strip()
                    if dep_name:
                        deps.append(dep_name)
            
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            if isinstance(poetry_deps, dict):
                for k in poetry_deps.keys():
                    if k.lower() != "python":
                        deps.append(k)

            manifest.dependencies.extend(deps)
        except Exception:
            pass

    if req_file.is_file() and not manifest.dependencies:
        try:
            with open(req_file, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        dep_name = re.split(r"[><=~!;]", line)[0].strip()
                        if dep_name:
                            manifest.dependencies.append(dep_name)
        except Exception:
            pass

    # Extract high-level stack tags
    dep_lower = {d.lower() for d in manifest.dependencies}
    known_stacks = {
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "pydantic": "Pydantic",
        "fastembed": "FastEmbed",
        "mcp": "MCP",
        "typer": "Typer",
        "rich": "Rich",
        "pytest": "Pytest",
        "torch": "PyTorch",
        "langchain": "LangChain",
        "langgraph": "LangGraph",
        "qdrant-client": "Qdrant",
    }
    for k, v in known_stacks.items():
        if k in dep_lower:
            manifest.stack_tags.append(v)

    return manifest


def parse_node_manifest(repo_path: Path) -> ParsedManifest:
    """Parse package.json and tsconfig.json."""
    manifest = ParsedManifest(languages=["JavaScript"])
    pkg_file = repo_path / "package.json"
    ts_file = repo_path / "tsconfig.json"

    if ts_file.is_file():
        manifest.languages.append("TypeScript")

    if pkg_file.is_file():
        try:
            with open(pkg_file, "r", encoding="utf-8", errors="replace") as f:
                data = json.load(f)

            manifest.name = data.get("name")
            manifest.version = data.get("version")
            manifest.description = data.get("description")

            all_deps = {}
            all_deps.update(data.get("dependencies", {}))
            all_deps.update(data.get("devDependencies", {}))

            manifest.dependencies = list(all_deps.keys())

            dep_lower = {d.lower() for d in manifest.dependencies}
            known_stacks = {
                "react": "React",
                "next": "Next.js",
                "vue": "Vue",
                "svelte": "Svelte",
                "express": "Express",
                "tailwindcss": "TailwindCSS",
                "typescript": "TypeScript",
                "vite": "Vite",
            }
            for k, v in known_stacks.items():
                if k in dep_lower and v not in manifest.stack_tags:
                    manifest.stack_tags.append(v)
        except Exception:
            pass

    return manifest


def parse_rust_manifest(repo_path: Path) -> ParsedManifest:
    """Parse Cargo.toml."""
    manifest = ParsedManifest(languages=["Rust"])
    cargo_file = repo_path / "Cargo.toml"

    if cargo_file.is_file():
        try:
            with open(cargo_file, "rb") as f:
                data = tomllib.load(f)

            pkg = data.get("package", {})
            manifest.name = pkg.get("name")
            manifest.version = pkg.get("version")
            manifest.description = pkg.get("description")

            deps = list(data.get("dependencies", {}).keys())
            manifest.dependencies = deps
            manifest.stack_tags.append("Rust")
        except Exception:
            pass

    return manifest


def parse_go_manifest(repo_path: Path) -> ParsedManifest:
    """Parse go.mod."""
    manifest = ParsedManifest(languages=["Go"])
    mod_file = repo_path / "go.mod"

    if mod_file.is_file():
        try:
            with open(mod_file, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("module "):
                        manifest.name = line.split("module ", 1)[1].strip().split("/")[-1]
                        break
            manifest.stack_tags.append("Golang")
        except Exception:
            pass

    return manifest


def parse_repository_manifest(repo_path: Path) -> ParsedManifest:
    """Aggregated manifest parser detecting all languages and dependencies."""
    combined = ParsedManifest()

    # 1. Python
    if (repo_path / "pyproject.toml").is_file() or (repo_path / "requirements.txt").is_file():
        py_man = parse_python_manifest(repo_path)
        combined.languages.extend([l for l in py_man.languages if l not in combined.languages])
        combined.stack_tags.extend([s for s in py_man.stack_tags if s not in combined.stack_tags])
        combined.dependencies.extend(py_man.dependencies)
        if not combined.name:
            combined.name = py_man.name
            combined.version = py_man.version
            combined.description = py_man.description

    # 2. Node / TS
    if (repo_path / "package.json").is_file():
        node_man = parse_node_manifest(repo_path)
        combined.languages.extend([l for l in node_man.languages if l not in combined.languages])
        combined.stack_tags.extend([s for s in node_man.stack_tags if s not in combined.stack_tags])
        combined.dependencies.extend(node_man.dependencies)
        if not combined.name:
            combined.name = node_man.name
            combined.version = node_man.version
            combined.description = node_man.description

    # 3. Rust
    if (repo_path / "Cargo.toml").is_file():
        rust_man = parse_rust_manifest(repo_path)
        combined.languages.extend([l for l in rust_man.languages if l not in combined.languages])
        combined.stack_tags.extend([s for s in rust_man.stack_tags if s not in combined.stack_tags])
        combined.dependencies.extend(rust_man.dependencies)
        if not combined.name:
            combined.name = rust_man.name

    # 4. Go
    if (repo_path / "go.mod").is_file():
        go_man = parse_go_manifest(repo_path)
        combined.languages.extend([l for l in go_man.languages if l not in combined.languages])
        combined.stack_tags.extend([s for s in go_man.stack_tags if s not in combined.stack_tags])
        if not combined.name:
            combined.name = go_man.name

    # 5. Containers / DevOps
    if (repo_path / "Dockerfile").is_file() or (repo_path / "docker-compose.yml").is_file() or (repo_path / "compose.yaml").is_file():
        if "Docker" not in combined.stack_tags:
            combined.stack_tags.append("Docker")

    if not combined.name:
        combined.name = repo_path.name

    return combined
