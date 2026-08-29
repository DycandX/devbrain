"""Repository Type Auto-Inspector and Ownership Classifier."""

from enum import Enum
from pathlib import Path
import subprocess
from typing import Optional, Tuple

from devbrain.harvester.manifest_parser import parse_repository_manifest


class RepoType(str, Enum):
    PROJECT = "project"            # Internal active project (10_Projects/)
    REFERENCE = "reference"        # Cloned external codebase for study (20_Knowledge/External_Repos/)
    SKILL = "skill"                # Agent skill / tool mesh (00_System/Agent_Skills/)
    KNOWLEDGE = "knowledge"        # Markdown docs / book / awesome-list (20_Knowledge/References/)
    UNKNOWN = "unknown"


def get_git_config_email() -> Optional[str]:
    """Retrieve local user's configured git email."""
    try:
        res = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0:
            return res.stdout.strip().lower()
    except Exception:
        pass
    return None


def get_repo_git_authors(repo_path: Path, max_commits: int = 10) -> Tuple[Optional[str], Optional[str]]:
    """Retrieve remote URL and list of recent author emails from git log."""
    remote_url = None
    recent_author_emails = []

    # Remote URL
    try:
        res_remote = subprocess.run(
            ["git", "-C", str(repo_path), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res_remote.returncode == 0:
            remote_url = res_remote.stdout.strip()
    except Exception:
        pass

    # Recent Author Emails
    try:
        res_log = subprocess.run(
            ["git", "-C", str(repo_path), "log", f"-n{max_commits}", "--pretty=format:%ae"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res_log.returncode == 0 and res_log.stdout.strip():
            recent_author_emails = [e.strip().lower() for e in res_log.stdout.splitlines() if e.strip()]
    except Exception:
        pass

    first_author = recent_author_emails[0] if recent_author_emails else None
    return remote_url, first_author


def inspect_repository_type(
    repo_path: Path,
    explicit_type: Optional[str] = None,
) -> Tuple[RepoType, str]:
    """Classify repository nature and return (RepoType, reason)."""
    repo_path = repo_path.resolve()
    if not repo_path.is_dir():
        return RepoType.UNKNOWN, "Target path is not a directory."

    if explicit_type:
        t_clean = explicit_type.strip().lower()
        if t_clean in [r.value for r in RepoType]:
            return RepoType(t_clean), f"Explicitly configured as {t_clean}."

    # 1. Check for Agent Skills
    if (repo_path / "SKILL.md").is_file() or (repo_path / "skills").is_dir():
        return RepoType.SKILL, "Contains SKILL.md or skills/ directory."

    # 2. Check for Pure Markdown Documentation / Knowledge
    all_files = [p for p in repo_path.rglob("*") if p.is_file() and not any(part.startswith(".") for part in p.parts)]
    if all_files:
        md_files = [p for p in all_files if p.suffix.lower() == ".md"]
        manifest_files = [p for p in all_files if p.name in ["package.json", "pyproject.toml", "Cargo.toml", "go.mod", "setup.py"]]
        
        if (len(md_files) / len(all_files) > 0.6) and not manifest_files:
            return RepoType.KNOWLEDGE, "Predominantly Markdown documents with no code manifests."

    # 3. Check for Code Manifests (Project vs Reference)
    manifest = parse_repository_manifest(repo_path)
    has_code = bool(manifest.dependencies or manifest.languages or (repo_path / ".git").is_dir())

    if has_code:
        # Check Git Author Heuristic
        user_email = get_git_config_email()
        remote_url, last_author = get_repo_git_authors(repo_path)

        path_lower = str(repo_path).lower()
        if any(keyword in path_lower for keyword in ["/learning/", "/references/", "/clones/", "/study/", "\\learning\\", "\\references\\"]):
            return RepoType.REFERENCE, "Located in a learning/references workspace directory."

        if user_email and last_author and (user_email in last_author or last_author in user_email):
            return RepoType.PROJECT, f"Git author '{last_author}' matches local git user."

        if not last_author and not remote_url:
            # Local new repository without git or fresh init
            return RepoType.PROJECT, "Local codebase with active code manifests."

        return RepoType.PROJECT, "Codebase with active build manifests."

    return RepoType.UNKNOWN, "Could not determine repository type."
