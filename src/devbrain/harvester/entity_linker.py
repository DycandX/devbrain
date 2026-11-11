"""Auto-Entity Linker and Graph Connector Engine for Obsidian."""

from datetime import datetime
from pathlib import Path
import re
from typing import Dict, Optional, Tuple

from devbrain.core.constants import DIR_PROJECTS
from devbrain.core.fsutil import atomic_write_text
from devbrain.engine.parser import parse_frontmatter


def catalog_known_projects(vault_path: Path) -> Dict[str, Tuple[str, Path]]:
    """Map normalized local paths to (project_name, project_readme_path)."""
    projects_dir = vault_path / DIR_PROJECTS
    mapping: Dict[str, Tuple[str, Path]] = {}

    if not projects_dir.is_dir():
        return mapping

    for readme_path in projects_dir.rglob("README.md"):
        try:
            with open(readme_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            frontmatter, _ = parse_frontmatter(content)
            local_path = frontmatter.get("local_path")
            proj_title = frontmatter.get("title") or readme_path.parent.name

            if local_path:
                norm_path = str(Path(local_path).resolve()).replace("\\", "/").lower()
                mapping[norm_path] = (proj_title, readme_path)
            # Also index project directory name
            mapping[readme_path.parent.name.lower()] = (proj_title, readme_path)
        except Exception:
            continue

    return mapping


def match_session_to_project(
    workspace_path_hint: Optional[str],
    vault_path: Path,
) -> Optional[Tuple[str, str]]:
    """Match a session's workspace path to an existing Project Hub in the vault.

    Returns:
        (project_title, relative_wikilink) e.g. ("Central AI Brain Hub", "10_Projects/_Central_AI_Brain_Hub/README")
    """
    if not workspace_path_hint:
        return None

    catalog = catalog_known_projects(vault_path)
    norm_hint = str(Path(workspace_path_hint).resolve()).replace("\\", "/").lower()

    # Exact or prefix match
    for known_path, (title, readme_file) in catalog.items():
        if known_path in norm_hint or norm_hint in known_path:
            rel_link = f"10_Projects/{readme_file.parent.name}/README"
            return title, rel_link

    # Name-based match
    hint_name = Path(workspace_path_hint).name.lower()
    for known_key, (title, readme_file) in catalog.items():
        if hint_name == known_key:
            rel_link = f"10_Projects/{readme_file.parent.name}/README"
            return title, rel_link

    return None


def generate_graph_links_block(
    created_time: datetime,
    matched_project: Optional[Tuple[str, str]] = None,
    device_name: Optional[str] = None,
) -> str:
    """Generate a clean markdown relations section to ensure graph connectivity.

    Daily notes are not linked: devbrain does not create them, and links to
    missing notes only add phantom nodes to the Obsidian graph.
    """
    lines = ["## 🔗 Graph Connections & Context:"]

    if matched_project:
        proj_title, proj_link = matched_project
        lines.append(f"- **Project Hub:** [[{proj_link}|{proj_title}]]")

    if device_name:
        lines.append(f"- **Device Origin:** `{device_name}`")

    return "\n".join(lines)


def inject_backlink_to_project(
    project_readme: Path,
    session_title: str,
    session_rel_path: str,
    created_date: str,
) -> bool:
    """Idempotently append a backlink to the project's README file."""
    if not project_readme.is_file():
        return False

    try:
        with open(project_readme, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        clean_rel = session_rel_path.replace("\\", "/")
        link_markdown = f"- [[{clean_rel}|{created_date} — {session_title}]]"

        if clean_rel in content:
            return False  # Already linked

        # Insert after the whole heading line, whatever follows the heading text
        heading = re.search(r"^## 📜 Riwayat Sesi AI Terkini[^\n]*$", content, re.MULTILINE)
        if heading:
            updated = content[: heading.end()] + f"\n{link_markdown}" + content[heading.end():]
        else:
            updated = content + f"\n\n## 📜 Riwayat Sesi AI Terkini\n{link_markdown}\n"

        atomic_write_text(project_readme, updated)
        return True
    except Exception:
        return False
