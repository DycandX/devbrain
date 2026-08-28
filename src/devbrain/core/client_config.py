"""Auto-configurator for registering devbrain FastMCP server in AI coding IDEs."""

import json
from pathlib import Path
import sys
from typing import Dict, List, Optional


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


def configure_antigravity(vault_path: Path) -> List[Path]:
    """Register central-brain server into Antigravity IDE configuration files."""
    updated_files: List[Path] = []
    server_block = get_server_command_block(vault_path)

    for cfg_path in get_antigravity_config_paths():
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if cfg_path.is_file():
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
            data["mcpServers"] = {}

        data["mcpServers"]["central-brain"] = server_block

        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        updated_files.append(cfg_path)

    return updated_files


def configure_claude(vault_path: Path) -> Optional[Path]:
    """Register central-brain server into Claude Code configuration file."""
    cfg_path = get_claude_config_path()
    server_block = get_server_command_block(vault_path)

    data = {}
    if cfg_path.is_file():
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
        data["mcpServers"] = {}

    data["mcpServers"]["central-brain"] = server_block

    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return cfg_path


def remove_all_mcp_configs() -> List[Path]:
    """Remove central-brain server entry from all known IDE config files."""
    cleaned_files: List[Path] = []
    all_paths = [*get_antigravity_config_paths(), get_claude_config_path()]

    for cfg_path in all_paths:
        if not cfg_path.is_file():
            continue

        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict) and "mcpServers" in data and isinstance(data["mcpServers"], dict):
                if "central-brain" in data["mcpServers"]:
                    del data["mcpServers"]["central-brain"]
                    with open(cfg_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    cleaned_files.append(cfg_path)
        except Exception:
            pass

    return cleaned_files
