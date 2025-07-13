"""
HK OpenAI Miscellaneous MCP Server module.

This module provides the core functionality for the HK OpenAI MCP Server,
including server creation and command-line interface setup.
"""

from fastmcp import FastMCP
from hkopenai.hk_misc_mcp_server import tool_auction
from typing import Dict, List, Annotated, Optional
from pydantic import Field


def create_mcp_server():
    """Create and configure the MCP server"""
    mcp = FastMCP(name="HK OpenAI misc Server")

    tool_auction.register(mcp)

    return mcp


def main(host: str, port: int, sse: bool):
    """
    Main function to start the MCP Server.
    
    Args:
        args: Command line arguments passed to the function.
    """
    server = create_mcp_server()

    if sse:
        server.run(transport="streamable-http", host=host, port=port)
        print(f"MCP Server running in SSE mode on port {args.port}, bound to {args.host}")
    else:
        server.run()
        print("MCP Server running in stdio mode")


if __name__ == "__main__":
    main()
