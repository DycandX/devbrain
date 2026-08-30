"""Configuration management for devbrain (.brainrc.json)."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

from devbrain.core.constants import (
    CONFIG_FILENAME,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_PROVIDER,
    DEFAULT_IGNORED_PATTERNS,
)


class BrainConfig(BaseModel):
    """Schema for vault configuration stored in .brainrc.json."""

    vault_path: str = Field(description="Absolute path to the Obsidian Vault directory")
    device_name: str = Field(default="local-device", description="Device identifier tag")
    embedding_provider: Literal["fastembed", "gemini", "openai", "ollama"] = Field(
        default=DEFAULT_EMBEDDING_PROVIDER,
        description="Active embedding engine provider",
    )
    embedding_model: str = Field(
        default=DEFAULT_EMBEDDING_MODEL,
        description="Name or ID of embedding model",
    )
    ollama_host: Optional[str] = Field(
        default=None,
        description="Host URL if using Ollama embedding",
    )
    ignored_paths: list[str] = Field(
        default_factory=lambda: list(DEFAULT_IGNORED_PATTERNS),
        description="List of file/folder patterns ignored by indexer",
    )
    scope: str = Field(
        default="all",
        description="Default partition scope (all, work, personal)",
    )
    workspace_roots: list[str] = Field(
        default_factory=list,
        description="Root directories to scan for Git repositories",
    )
    linked_vaults: dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping alias -> absolute directory path of external linked vaults",
    )
    custom_skill_roots: list[str] = Field(
        default_factory=list,
        description="Custom external skill root directories",
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of vault initialization",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO timestamp of last configuration update",
    )

    def resolve_vault_path(self) -> Path:
        """Returns the resolved Path object for the vault."""
        return Path(self.vault_path).resolve()

    def resolve_linked_vaults(self) -> dict[str, Path]:
        """Returns dictionary of alias -> resolved Path object for each linked vault."""
        return {alias: Path(p).resolve() for alias, p in self.linked_vaults.items()}


def find_config(start_path: Optional[Path] = None) -> Optional[Path]:
    """Search for .brainrc.json in current directory or parent directories."""
    curr = (start_path or Path.cwd()).resolve()
    for parent in [curr, *curr.parents]:
        config_candidate = parent / CONFIG_FILENAME
        if config_candidate.is_file():
            return config_candidate
    return None


def load_config(path_or_dir: Path) -> BrainConfig:
    """Load and parse .brainrc.json from a file path or directory."""
    path = path_or_dir.resolve()
    if path.is_dir():
        config_file = path / CONFIG_FILENAME
    else:
        config_file = path

    if not config_file.is_file():
        raise FileNotFoundError(f"Configuration file not found at: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return BrainConfig(**data)


def save_config(config: BrainConfig, path_or_dir: Path) -> Path:
    """Save configuration to .brainrc.json."""
    path = path_or_dir.resolve()
    if path.is_dir():
        config_file = path / CONFIG_FILENAME
    else:
        config_file = path

    config.updated_at = datetime.now(timezone.utc).isoformat()
    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)

    return config_file
