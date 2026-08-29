"""Project & Workspace Harvester for Auto-Seeding Repositories into Obsidian with Codebase Synthesis."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Dict, List, Optional

from devbrain.core.constants import DIR_AGENT_SKILLS, DIR_KNOWLEDGE, DIR_PROJECTS
from devbrain.engine.hybrid_search import HybridEngine
from devbrain.harvester.inspector import RepoType, inspect_repository_type
from devbrain.harvester.manifest_parser import ParsedManifest, parse_repository_manifest
from devbrain.harvester.tree_analyzer import analyze_codebase_structure


@dataclass
class ScannedProjectMetadata:
    """Consolidated metadata extracted from a local repository."""
    name: str
    clean_name: str
    repo_path: Path
    repo_type: RepoType
    type_reason: str
    description: str
    languages: List[str]
    stack_tags: List[str]
    dependencies: List[str]
    scripts: Dict[str, str] = field(default_factory=dict)
    entrypoints: List[str] = field(default_factory=list)
    infra_files: List[str] = field(default_factory=list)
    ascii_tree: Optional[str] = None
    subproject_dirs: List[Path] = field(default_factory=list)
    git_remote: Optional[str] = None
    git_branch: Optional[str] = None
    last_commit_time: Optional[datetime] = None
    readme_excerpt: Optional[str] = None


def extract_git_branch(repo_path: Path) -> Optional[str]:
    """Get active git branch name."""
    try:
        res = subprocess.run(
            ["git", "-C", str(repo_path), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return None


def extract_readme_excerpt(repo_path: Path, max_length: int = 1500) -> Optional[str]:
    """Read overview from root README.md."""
    for candidate in ["README.md", "readme.md", "README.MD"]:
        f = repo_path / candidate
        if f.is_file():
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as stream:
                    text = stream.read()
                cleaned = re.sub(r"^#+\s*.*", "", text).strip()
                if len(cleaned) > max_length:
                    cleaned = cleaned[:max_length].rstrip() + "..."
                return cleaned
            except Exception:
                pass
    return None


def scan_project_metadata(
    repo_path: Path,
    explicit_type: Optional[str] = None,
) -> ScannedProjectMetadata:
    """Scan and synthesize all metadata from a repository directory."""
    repo_path = repo_path.resolve()
    repo_type, reason = inspect_repository_type(repo_path, explicit_type=explicit_type)
    manifest = parse_repository_manifest(repo_path)
    analysis = analyze_codebase_structure(repo_path)

    # Git details
    branch = extract_git_branch(repo_path)
    remote = None
    try:
        res_remote = subprocess.run(
            ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res_remote.returncode == 0:
            remote = res_remote.stdout.strip()
    except Exception:
        pass

    readme_text = extract_readme_excerpt(repo_path)

    # Smart Overview Synthesis if no README is present
    if manifest.description:
        raw_desc = manifest.description
    elif readme_text:
        raw_desc = readme_text[:250]
    else:
        # Synthesize from codebase structure
        lang_str = ", ".join(manifest.languages) or "Software"
        stack_str = ", ".join(manifest.stack_tags) or "Standard"
        parts = [f"Auto-synthesized {lang_str} codebase ({stack_str})."]
        if analysis.entrypoints:
            parts.append(f"Entrypoint: {', '.join(analysis.entrypoints)}.")
        if analysis.infra_files:
            parts.append(f"Infrastructure: {', '.join(analysis.infra_files)}.")
        raw_desc = " ".join(parts)

    clean_desc = re.sub(r"\s+", " ", raw_desc).strip().replace('"', "'")
    clean_name = re.sub(r"[^\w\-_]", "_", manifest.name or repo_path.name).strip("_")

    return ScannedProjectMetadata(
        name=manifest.name or repo_path.name,
        clean_name=clean_name,
        repo_path=repo_path,
        repo_type=repo_type,
        type_reason=reason,
        description=clean_desc,
        languages=manifest.languages or ["Markdown"],
        stack_tags=manifest.stack_tags,
        dependencies=manifest.dependencies[:30],
        scripts=manifest.scripts,
        entrypoints=analysis.entrypoints,
        infra_files=analysis.infra_files,
        ascii_tree=analysis.ascii_tree,
        subproject_dirs=analysis.subproject_dirs,
        git_remote=remote,
        git_branch=branch,
        readme_excerpt=readme_text,
    )


def seed_project_to_vault(
    metadata: ScannedProjectMetadata,
    vault_path: Path,
) -> Path:
    """Seed structured Markdown notes or skills into the Obsidian Vault with smart synthesis."""
    vault_path = vault_path.resolve()
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. Active Project Seeding -> 10_Projects/<Project_Name>/README.md
    if metadata.repo_type == RepoType.PROJECT:
        target_dir = vault_path / DIR_PROJECTS / metadata.clean_name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "README.md"

        langs_json = json.dumps(metadata.languages)
        stack_json = json.dumps(metadata.stack_tags)
        deps_list = "\n".join([f"- `{d}`" for d in metadata.dependencies[:15]]) or "- *No external dependencies detected.*"

        scripts_list = ""
        if metadata.scripts:
            scripts_list = "\n## ⚡ Runnable Scripts:\n" + "\n".join([
                f"- `{cmd}` → `{script}`" if cmd != script else f"- `{cmd}`"
                for cmd, script in list(metadata.scripts.items())[:8]
            ]) + "\n\n---"

        tree_block = ""
        if metadata.ascii_tree:
            tree_block = f"\n## 🌳 Project Structure:\n```text\n{metadata.ascii_tree}\n```\n\n---"

        entrypoints_line = f"\n> **Entrypoints:** `{'` | `'.join(metadata.entrypoints)}`" if metadata.entrypoints else ""

        content = f"""---
id: "PROJ-{metadata.clean_name.upper()}"
title: "{metadata.name}"
type: "project"
role: "owner"
status: "active"
language: {langs_json}
stack: {stack_json}
git_remote: "{metadata.git_remote or ''}"
local_path: "{str(metadata.repo_path).replace('\\', '/')}"
last_scanned: "{now_iso}"
tags: ["project", "codebase"]
---

# 🚀 {metadata.name}

> **Local Path:** `{str(metadata.repo_path)}`  
> **Git Remote:** `{metadata.git_remote or 'Local Repository'}` {f'(`branch: {metadata.git_branch}`)' if metadata.git_branch else ''}  
> **Tech Stack:** `{'` | `'.join(metadata.stack_tags) if metadata.stack_tags else 'Standard'}`{entrypoints_line}

## 📋 Overview
{metadata.description}

---
{scripts_list}
{tree_block}
## 🛠️ Key Dependencies & Manifests:
{deps_list}

---

## 📜 Riwayat Sesi AI Terkini (Live Dataview):
```dataview
TABLE created, device, title
FROM "90_Agent_Inbox"
WHERE contains(file.text, "{metadata.clean_name}") OR contains(file.text, "{metadata.name}")
SORT created DESC
LIMIT 10
```
"""
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

    # 2. Cloned External Reference -> 20_Knowledge/External_Repos/<Repo>/README.md
    elif metadata.repo_type == RepoType.REFERENCE:
        target_dir = vault_path / DIR_KNOWLEDGE / "External_Repos" / metadata.clean_name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "README.md"

        langs_json = json.dumps(metadata.languages)
        stack_json = json.dumps(metadata.stack_tags)

        tree_block = f"\n## 🌳 Repository Structure:\n```text\n{metadata.ascii_tree}\n```\n" if metadata.ascii_tree else ""

        content = f"""---
id: "REF-{metadata.clean_name.upper()}"
title: "{metadata.name} (Code Reference)"
type: "reference-repo"
role: "study"
language: {langs_json}
stack: {stack_json}
git_remote: "{metadata.git_remote or ''}"
local_path: "{str(metadata.repo_path).replace('\\', '/')}"
last_scanned: "{now_iso}"
tags: ["reference", "code-study", "external-repo"]
---

# 📚 Reference: {metadata.name}

> **Source Repository:** `{metadata.git_remote or str(metadata.repo_path)}`  
> **Type:** External Open-Source Study Codebase

## 📋 Architectural Overview:
{metadata.description}

## 🛠️ Tech Stack & Patterns:
`{'` | `'.join(metadata.stack_tags) if metadata.stack_tags else 'Standard'}`
{tree_block}
"""
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

    # 3. Agent Skill -> 00_System/Agent_Skills/<skill>/
    elif metadata.repo_type == RepoType.SKILL:
        target_dir = vault_path / DIR_AGENT_SKILLS / metadata.clean_name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "SKILL.md"

        src_skill = metadata.repo_path / "SKILL.md"
        if src_skill.is_file():
            shutil.copy2(src_skill, target_file)
        else:
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(f"""---
name: {metadata.clean_name}
description: {metadata.description}
---

# {metadata.name} Skill

{metadata.description}
""")

    # 4. Knowledge Docs -> 20_Knowledge/References/<Repo>/
    else:
        target_dir = vault_path / DIR_KNOWLEDGE / "References" / metadata.clean_name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "README.md"

        tree_block = f"\n## 🌳 Directory Structure:\n```text\n{metadata.ascii_tree}\n```\n" if metadata.ascii_tree else ""

        content = f"""---
id: "DOC-{metadata.clean_name.upper()}"
title: "{metadata.name} Documentation"
type: "knowledge-doc"
last_scanned: "{now_iso}"
tags: ["knowledge", "documentation"]
---

# 📖 {metadata.name}

{metadata.description}
{tree_block}
{metadata.readme_excerpt or ''}
"""
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

    # Trigger FastEmbed & BM25 re-indexing
    try:
        engine = HybridEngine(vault_path=vault_path)
        engine.initialize()
        engine.index_vault(force_reindex=False)
    except Exception:
        pass

    return target_file
