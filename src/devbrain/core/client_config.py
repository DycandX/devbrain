"""Auto-configurator for registering devbrain FastMCP server in AI coding IDEs."""

import json
from pathlib import Path
import sys
from typing import Dict, List, Optional

from devbrain.core.fsutil import atomic_write_json

MCP_SERVER_NAME = "central-brain"


def get_antigravity_config_paths() -> List[Path]:
    """Find potential Antigravity IDE configuration files."""
    home = Path.home()
    candidates = [
        home / ".gemini" / "antigravity" / "mcp_config.json",
        home / ".gemini" / "antigravity-ide" / "mcp_config.json",
        home / ".gemini" / "config" / "mcp_config.json",
    ]
    return candidates


def get_claude_config_path() -> Path:
    """Find Claude Code configuration file."""
    return Path.home() / ".claude.json"


def get_server_command_block(vault_path: Path) -> Dict:
    """Generate the standard JSON-RPC command block for MCP server execution."""
    python_exec = sys.executable
    return {
        "command": python_exec,
        "args": [
            "-m",
            "devbrain.cli.main",
            "serve",
            "--stdio",
            "--vault",
            str(vault_path.resolve()),
        ],
    }


def _read_config(cfg_path: Path) -> Optional[dict]:
    """Load an IDE config file.

    Returns {} when the file does not exist, and None when it exists but cannot
    be parsed, so callers never overwrite a config they failed to read.
    """
    if not cfg_path.is_file():
        return {}
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _register_server(cfg_path: Path, server_block: Dict) -> bool:
    """Add or update the central-brain entry in one config file, keeping other entries."""
    data = _read_config(cfg_path)
    if data is None:
        return False

    if not isinstance(data.get("mcpServers"), dict):
        data["mcpServers"] = {}
    data["mcpServers"][MCP_SERVER_NAME] = server_block

    atomic_write_json(cfg_path, data)
    return True


def configure_antigravity(vault_path: Path) -> List[Path]:
    """Register central-brain server into Antigravity IDE configuration files.

    Only config locations whose directory already exists are touched. When none
    exists, the primary location is created.
    """
    server_block = get_server_command_block(vault_path)
    candidates = get_antigravity_config_paths()
    targets = [p for p in candidates if p.parent.is_dir()] or candidates[:1]

    return [cfg_path for cfg_path in targets if _register_server(cfg_path, server_block)]


def configure_claude(vault_path: Path) -> Optional[Path]:
    """Register central-brain server into Claude Code configuration file.

    Returns None when the existing file could not be parsed and was left untouched.
    """
    cfg_path = get_claude_config_path()
    if _register_server(cfg_path, get_server_command_block(vault_path)):
        return cfg_path
    return None


def remove_all_mcp_configs() -> List[Path]:
    """Remove central-brain server entry from all known IDE config files."""
    cleaned_files: List[Path] = []
    all_paths = [*get_antigravity_config_paths(), get_claude_config_path()]

    for cfg_path in all_paths:
        data = _read_config(cfg_path)
        if not data:
            continue

        servers = data.get("mcpServers")
        if isinstance(servers, dict) and MCP_SERVER_NAME in servers:
            del servers[MCP_SERVER_NAME]
            atomic_write_json(cfg_path, data)
            cleaned_files.append(cfg_path)

    return cleaned_files
