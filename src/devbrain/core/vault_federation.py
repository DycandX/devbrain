"""Vault Federation Manager: Manage linking, unlinking, mounting, and discovery of external vaults."""

from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import Optional

from devbrain.core.config import BrainConfig, load_config, save_config

LINKED_VAULTS_DIR = Path("20_Knowledge") / "Linked_Vaults"


@dataclass
class LinkedVaultInfo:
    """Metadata and inspection status for a linked external vault."""

    alias: str
    target_path: Path
    exists: bool
    note_count: int
    is_mounted: bool
    mount_path: Optional[Path] = None


def sanitize_alias(raw_alias: str) -> str:
    """Sanitize vault alias to alphanumeric + dashes/underscores."""
    clean = re.sub(r"[^a-zA-Z0-9_-]", "_", raw_alias.strip().lower())
    clean = re.sub(r"_+", "_", clean).strip("_")
    return clean or "vault"


def create_directory_mount(target_dir: Path, mount_point: Path) -> bool:
    """Create Windows Directory Junction or POSIX Symlink for non-destructive mounting."""
    mount_point.parent.mkdir(parents=True, exist_ok=True)

    # If mount point already exists, remove existing junction/symlink first
    remove_directory_mount(mount_point)

    # Windows Directory Junction (does not require admin privileges)
    if os.name == "nt":
        try:
            import _winapi

            _winapi.CreateJunction(str(target_dir.resolve()), str(mount_point))
            return True
        except Exception:
            try:
                os.symlink(str(target_dir.resolve()), str(mount_point), target_is_directory=True)
                return True
            except Exception:
                return False
    else:
        try:
            os.symlink(str(target_dir.resolve()), str(mount_point), target_is_directory=True)
            return True
        except Exception:
            return False


def remove_directory_mount(mount_point: Path) -> bool:
    """Safely remove a directory junction or symlink without deleting target files."""
    mount_str = str(mount_point)
    if not os.path.exists(mount_str) and not os.path.islink(mount_str):
        return False

    try:
        if os.name == "nt":
            # On Windows, os.rmdir on an un-resolved junction path safely deletes the junction entry
            os.rmdir(mount_str)
            return True
        else:
            mount_point.unlink()
            return True
    except Exception:
        try:
            mount_point.unlink()
            return True
        except Exception:
            return False


class VaultFederationManager:
    """Service to coordinate multi-vault federation and directory mounting."""

    def __init__(self, vault_path: Path, config: Optional[BrainConfig] = None):
        self.vault_path = vault_path.resolve()
        self.config = config or load_config(self.vault_path)

    def link_vault(
        self,
        target_path: Path,
        alias: Optional[str] = None,
        mount: bool = False,
    ) -> tuple[str, Path, bool]:
        """Link an external vault into Central Brain federation.

        Returns: (alias, resolved_target_path, is_mounted)
        """
        resolved_target = target_path.resolve()
        if not resolved_target.is_dir():
            raise FileNotFoundError(f"Target directory does not exist: {resolved_target}")

        if resolved_target == self.vault_path:
            raise ValueError("Cannot link Central Brain vault to itself.")

        chosen_alias = sanitize_alias(alias or resolved_target.name)

        # 1. Update config
        self.config.linked_vaults[chosen_alias] = str(resolved_target)
        save_config(self.config, self.vault_path)

        # 2. Handle directory junction mount
        is_mounted = False
        if mount:
            mount_dir = self.vault_path / LINKED_VAULTS_DIR / chosen_alias
            is_mounted = create_directory_mount(resolved_target, mount_dir)

        return chosen_alias, resolved_target, is_mounted

    def unlink_vault(self, alias: str, clean_mount: bool = True) -> bool:
        """Unlink an external vault and clean up mount junctions."""
        clean_alias = sanitize_alias(alias)
        if clean_alias not in self.config.linked_vaults:
            return False

        # Remove from config
        del self.config.linked_vaults[clean_alias]
        save_config(self.config, self.vault_path)

        # Clean junction mount if exists
        if clean_mount:
            mount_dir = self.vault_path / LINKED_VAULTS_DIR / clean_alias
            remove_directory_mount(mount_dir)

        return True

    def list_linked_vaults(self) -> list[LinkedVaultInfo]:
        """List all linked external vaults with status, note count, and mount information."""
        results: list[LinkedVaultInfo] = []

        for alias, path_str in self.config.linked_vaults.items():
            target_p = Path(path_str).resolve()
            exists = target_p.is_dir()
            note_count = 0
            if exists:
                try:
                    note_count = len(list(target_p.rglob("*.md")))
                except Exception:
                    note_count = 0

            mount_p = self.vault_path / LINKED_VAULTS_DIR / alias
            is_mounted = os.path.exists(str(mount_p)) or os.path.islink(str(mount_p))

            results.append(
                LinkedVaultInfo(
                    alias=alias,
                    target_path=target_p,
                    exists=exists,
                    note_count=note_count,
                    is_mounted=is_mounted,
                    mount_path=mount_p if is_mounted else None,
                )
            )

        return results
