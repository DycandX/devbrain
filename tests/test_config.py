"""Tests for configuration load/save and schema validation."""

import pytest
from pathlib import Path

from devbrain.core.config import BrainConfig, load_config, save_config, find_config
from devbrain.core.constants import CONFIG_FILENAME


def test_brain_config_defaults(tmp_path: Path):
    vault_dir = tmp_path / "MyVault"
    config = BrainConfig(vault_path=str(vault_dir))
    
    assert config.vault_path == str(vault_dir)
    assert config.embedding_provider == "fastembed"
    assert config.scope == "all"
    assert len(config.ignored_paths) > 0


def test_save_and_load_config(tmp_path: Path):
    vault_dir = tmp_path / "MyVault"
    vault_dir.mkdir()
    
    original_config = BrainConfig(
        vault_path=str(vault_dir),
        device_name="test-laptop",
        embedding_provider="fastembed",
        embedding_model="BAAI/bge-small-en-v1.5",
    )
    
    config_file = save_config(original_config, vault_dir)
    assert config_file.is_file()
    assert config_file.name == CONFIG_FILENAME
    
    loaded_config = load_config(vault_dir)
    assert loaded_config.vault_path == original_config.vault_path
    assert loaded_config.device_name == "test-laptop"
    assert loaded_config.embedding_provider == "fastembed"


def test_find_config(tmp_path: Path):
    vault_dir = tmp_path / "Deep" / "Nested" / "Vault"
    vault_dir.mkdir(parents=True)
    
    config = BrainConfig(vault_path=str(vault_dir))
    save_config(config, vault_dir)
    
    # Search from inside a subfolder
    sub_dir = vault_dir / "10_Projects"
    sub_dir.mkdir()
    
    found = find_config(sub_dir)
    assert found is not None
    assert found.parent == vault_dir
