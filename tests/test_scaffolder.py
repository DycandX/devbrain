"""Tests for vault scaffolder matching 07 taxonomy."""

from pathlib import Path
from devbrain.core.scaffolder import scaffold_vault
from devbrain.core.constants import (
    DIR_SYSTEM,
    DIR_SYSTEM_RULES,
    DIR_SYSTEM_PERSONAS,
    DIR_AGENT_SKILLS,
    DIR_PROJECTS,
    DIR_KNOWLEDGE,
    DIR_KNOWLEDGE_ARCH,
    DIR_DECISIONS,
    DIR_INBOX,
    DIR_DAILY,
    BRAIN_IGNORE_FILENAME,
)


def test_scaffold_vault_creates_structure(tmp_path: Path):
    vault_dir = tmp_path / "TestVault"
    created = scaffold_vault(vault_dir, is_new=True)
    
    assert (vault_dir / DIR_SYSTEM).is_dir()
    assert (vault_dir / DIR_SYSTEM_RULES).is_dir()
    assert (vault_dir / DIR_SYSTEM_PERSONAS).is_dir()
    assert (vault_dir / DIR_AGENT_SKILLS).is_dir()
    assert (vault_dir / DIR_PROJECTS).is_dir()
    assert (vault_dir / DIR_KNOWLEDGE).is_dir()
    assert (vault_dir / DIR_KNOWLEDGE_ARCH).is_dir()
    assert (vault_dir / DIR_DECISIONS).is_dir()
    assert (vault_dir / DIR_INBOX).is_dir()
    assert (vault_dir / DIR_DAILY).is_dir()
    
    assert (vault_dir / DIR_SYSTEM / "global_context.md").is_file()
    assert (vault_dir / DIR_SYSTEM_RULES / "general_rules.md").is_file()
    assert (vault_dir / DIR_DECISIONS / "ADR-001-use-fastmcp-and-fastembed.md").is_file()
    assert (vault_dir / DIR_AGENT_SKILLS / "example_skill" / "SKILL.md").is_file()
    assert (vault_dir / BRAIN_IGNORE_FILENAME).is_file()
    assert len(created) > 0


def test_scaffold_vault_non_destructive(tmp_path: Path):
    vault_dir = tmp_path / "ExistingVault"
    vault_dir.mkdir()
    
    # Create custom global_context.md beforehand
    custom_context = vault_dir / DIR_SYSTEM / "global_context.md"
    custom_context.parent.mkdir(parents=True)
    custom_context.write_text("CUSTOM CONTEXT CONTENT")
    
    scaffold_vault(vault_dir, is_new=False)
    
    # Ensure custom content was NOT overwritten
    assert custom_context.read_text() == "CUSTOM CONTEXT CONTENT"
