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
