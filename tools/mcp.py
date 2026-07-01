"""
MCP tool registry — singleton.

Call ``await initialize_mcp_tools()`` once at startup.
Afterwards ``get_mcp_tools()`` returns the cached list synchronously.
The MultiServerMCPClient is kept alive so tool calls remain valid.
"""
import os
import time
from typing import Any
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

_mcp_client: MultiServerMCPClient | None = None
_mcp_tools: list[Any] | None = None

_MCP_CONFIG = {
    "jira": {
        "transport": "stdio",
        "command": "npx.cmd",
        "args": ["-y", "mcp-jira-stdio"],
        "env": {
            "JIRA_BASE_URL": os.getenv("JIRA_BASE_URL"),
            "JIRA_EMAIL": os.getenv("JIRA_EMAIL"),
            "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN"),
        },
    },
    "slack": {
        "transport": "stdio",
        "command": "npx.cmd",
        "args": ["-y", "@modelcontextprotocol/server-slack"],
        "env": {
            "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
            "SLACK_TEAM_ID": os.getenv("SLACK_TEAM_ID"),
        },
    },
    "gmail": {
        "transport": "stdio",
        "command": "npx.cmd",
        "args": ["-y", "@gongrzhe/server-gmail-autoauth-mcp"],
        "env": {
            "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
            "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
        },
    },
    "calendar": {
        "transport": "stdio",
        "command": "npx.cmd",
        "args": ["-y", "@gongrzhe/server-calendar-autoauth-mcp"],
        "env": {
            "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
            "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
        },
    },
}


async def initialize_mcp_tools() -> list[Any]:
    """Load MCP tools exactly once and cache them.  Safe to call multiple times."""
    start_time = time.perf_counter()
    global _mcp_client, _mcp_tools
    if _mcp_tools is not None:
        return _mcp_tools
    _mcp_client = MultiServerMCPClient(_MCP_CONFIG)
    _mcp_tools = await _mcp_client.get_tools()
    end_time = time.perf_counter()
    print(f"MCP tools initialized in {end_time - start_time:.2f} seconds.")
    return _mcp_tools


def get_mcp_tools() -> list[Any]:
    """Return the cached MCP tools (synchronous).

    Raises RuntimeError if ``initialize_mcp_tools()`` has not been awaited yet.
    """
    if _mcp_tools is None:
        raise RuntimeError(
            "MCP tools are not initialized. "
            "Await initialize_mcp_tools() before running the graph."
        )
    return _mcp_tools

