"""
Unit tests for the MCP server functionality.

This module tests the creation and configuration of the MCP server.
"""

import unittest
from unittest.mock import patch, Mock
from hkopenai.hk_misc_mcp_server.server import server


class TestApp(unittest.TestCase):
    """
    Test class for MCP server application.

    This class contains test cases for verifying the correct setup and behavior
    of the MCP server.
    """

    @patch("hkopenai.hk_misc_mcp_server.server.FastMCP")
    @patch("hkopenai.hk_misc_mcp_server.server.auction")
    def test_server(self, mock_auction, mock_fastmcp):
        """
        Test the creation of the MCP server.

        This test verifies that the MCP server is created correctly with the expected
        tool configurations and that the underlying functions are called as expected.
        """
        # Setup mocks
        mock_mcp = Mock()

        # Configure mock_mcp.tool to return a mock that acts as the decorator
        # This mock will then be called with the function to be decorated
        mock_mcp.tool.return_value = Mock()
        mock_fastmcp.return_value = mock_mcp

        # Test server creation
        mcp = server()

        # Verify server creation
        mock_fastmcp.assert_called_once()
        self.assertEqual(mcp, mock_mcp)

        mock_auction.register.assert_called_once_with(mock_mcp)


if __name__ == "__main__":
    unittest.main()
