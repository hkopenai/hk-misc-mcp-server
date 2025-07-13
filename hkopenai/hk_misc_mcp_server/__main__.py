"""
Main entry point for the HK Misc MCP Server.

This module serves as the entry point to start the MCP server.
"""



from hkopenai_common.cli_utils import cli_main
from .server import server

if __name__ == "__main__":
    cli_main(server, "HK Misc MCP Server")