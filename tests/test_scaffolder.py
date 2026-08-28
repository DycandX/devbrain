"""Tests for vault scaffolder."""

from pathlib import Path
from devbrain.core.scaffolder import scaffold_vault
from devbrain.core.constants import (
    DIR_SYSTEM,
    DIR_AGENT_SKILLS,
    DIR_PROJECTS,
    DIR_KNOWLEDGE,
    DIR_INBOX,
    BRAIN_IGNORE_FILENAME,
)


def test_scaffold_vault_creates_structure(tmp_path: Path):
    vault_dir = tmp_path / "TestVault"
    created = scaffold_vault(vault_dir, is_new=True)
    
    assert (vault_dir / DIR_SYSTEM).is_dir()
    assert (vault_dir / DIR_AGENT_SKILLS).is_dir()
    assert (vault_dir / DIR_PROJECTS).is_dir()
    assert (vault_dir / DIR_KNOWLEDGE).is_dir()
    assert (vault_dir / DIR_INBOX).is_dir()
    
    assert (vault_dir / DIR_SYSTEM / "rules.md").is_file()
    assert (vault_dir / DIR_AGENT_SKILLS / "example_skill" / "SKILL.md").is_file()
    assert (vault_dir / BRAIN_IGNORE_FILENAME).is_file()
    assert len(created) > 0


def test_scaffold_vault_non_destructive(tmp_path: Path):
    vault_dir = tmp_path / "ExistingVault"
    vault_dir.mkdir()
    
    # Create custom rules.md beforehand
    custom_rules = vault_dir / DIR_SYSTEM / "rules.md"
    custom_rules.parent.mkdir(parents=True)
    custom_rules.write_text("CUSTOM RULES CONTENT")
    
    scaffold_vault(vault_dir, is_new=False)
    
    # Ensure custom content was NOT overwritten
    assert custom_rules.read_text() == "CUSTOM RULES CONTENT"
