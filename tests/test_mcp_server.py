"""Tests for FastMCP Server and the 4 Core Memory Tools."""

import asyncio
from pathlib import Path
from devbrain.core.config import BrainConfig, save_config
from devbrain.core.constants import DIR_INBOX
from devbrain.core.scaffolder import scaffold_vault
from devbrain.mcp_server.server import create_mcp_server


def test_mcp_server_initialization_and_tool_execution(tmp_path: Path):
    vault = tmp_path / "McpTestVault"
    scaffold_vault(vault, is_new=True)

    config = BrainConfig(vault_path=str(vault), device_name="test-machine")
    save_config(config, vault)

    server = create_mcp_server(vault, config=config)
    assert server.name == "central-brain"

    # Verify all 4 tools are registered
    tools_list = asyncio.run(server.list_tools())
    tool_names = [t.name for t in tools_list]
    assert "search_brain" in tool_names
    assert "get_project_context" in tool_names
    assert "write_agent_log" in tool_names
    assert "load_skill" in tool_names

    # 1. Test get_project_context tool
    ctx = asyncio.run(server.call_tool("get_project_context", {"project_name": "example_project"}))
    ctx_text = ctx[0].text if isinstance(ctx, list) else str(ctx)
    assert "Example Project" in ctx_text

    # 2. Test load_skill tool
    skill_res = asyncio.run(server.call_tool("load_skill", {"skill_name": "example_skill"}))
    skill_text = skill_res[0].text if isinstance(skill_res, list) else str(skill_res)
    assert "Example Workflow Skill" in skill_text

    # 3. Test write_agent_log tool
    log_res = asyncio.run(server.call_tool("write_agent_log", {
        "summary": "Completed Unit Test Session",
        "details": "All unit tests for FastMCP were executed successfully.",
        "tags": ["unit-test", "mcp"],
        "author": "antigravity-test",
    }))
    log_text = log_res[0].text if isinstance(log_res, list) else str(log_res)
    assert "Successfully recorded agent log" in log_text

    # Verify file was actually created on disk
    inbox_files = list((vault / DIR_INBOX).glob("*.md"))
    # Exclude _Inbox_Index.md
    log_files = [f for f in inbox_files if not f.name.startswith("_")]
    assert len(log_files) >= 1

    # 4. Test search_brain tool
    search_res = asyncio.run(server.call_tool("search_brain", {"query": "Clean Architecture", "limit": 2}))
    search_text = search_res[0].text if isinstance(search_res, list) else str(search_res)
    assert "Clean & Modular Architecture" in search_text or "20_Knowledge" in search_text
