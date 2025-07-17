"""
HK OpenAI Miscellaneous MCP Server module.

This module provides the core functionality for the HK OpenAI MCP Server,
including server creation and command-line interface setup.
"""

from fastmcp import FastMCP
from .tools import auction


def server():
    """Create and configure the MCP server"""
    mcp = FastMCP(name="HK OpenAI misc Server")

    auction.register(mcp)

    return mcp
