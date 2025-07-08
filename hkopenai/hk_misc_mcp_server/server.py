"""
HK OpenAI Miscellaneous MCP Server module.

This module provides the core functionality for the HK OpenAI MCP Server,
including server creation and command-line interface setup.
"""

import argparse
from fastmcp import FastMCP
from hkopenai.hk_misc_mcp_server import tool_auction
from typing import Dict, List, Annotated, Optional
from pydantic import Field


def create_mcp_server():
    """Create and configure the MCP server"""
    mcp = FastMCP(name="HK OpenAI misc Server")

    @mcp.tool(
        description="Auction data of confiscated, used/surplus, and unclaimed stores from Government Logistics Department Hong Kong."
    )
    def get_auction_data(
        start_year: Annotated[
            int, Field(description="Starting year for the data range")
        ],
        start_month: Annotated[
            int, Field(description="Starting month for the data range")
        ],
        end_year: Annotated[int, Field(description="Ending year for the data range")],
        end_month: Annotated[int, Field(description="Ending month for the data range")],
        language: Annotated[
            str, Field(description="Language code for the data ('EN', 'TC', 'SC')")
        ],
    ) -> List[Dict]:
        return tool_auction.get_auction_data(
            start_year, start_month, end_year, end_month, language
        )

    return mcp


def main():
    """
    Main function to start the MCP Server.
    
    Parses command-line arguments to determine the mode of operation (SSE or stdio)
    and starts the server accordingly.
    """
    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument(
        "-s", "--sse", action="store_true", help="Run in SSE mode instead of stdio"
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to bind the server to"
    )
    args = parser.parse_args()

    server = create_mcp_server()

    if args.sse:
        server.run(transport="streamable-http", host=args.host)
        print(f"MCP Server running in SSE mode on port 8000, bound to {args.host}")
    else:
        server.run()
        print("MCP Server running in stdio mode")


if __name__ == "__main__":
    main()
