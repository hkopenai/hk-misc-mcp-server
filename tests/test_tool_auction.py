"""
Module for testing the government auction data tool functionality.

This module contains unit tests for fetching and processing government auction data.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from hkopenai.hk_misc_mcp_server.tools.auction import (
    _get_government_auction_data,
    register,
)


class TestGovernmentAuctionData(unittest.TestCase):
    """
    Test class for verifying government auction data functionality.

    This class contains test cases to ensure the data fetching and processing
    for government auction data work as expected.
    """

    def test_get_government_auction_data(self):
        """
        Test the retrieval and filtering of government auction data.

        This test verifies that the function correctly fetches and filters data by date range,
        and handles error cases.
        """
        # Mock the CSV data
        mock_csv_data = [
            {
                "Date of Auction": "01/01/2023",
                "Auction List No.": "24",
                "Lot No.": "1",
                "Description": "Item A",
                "Quantity": "10",
                "Unit": "pcs",
            },
            {
                "Date of Auction": "15/01/2023",
                "Auction List No.": "24",
                "Lot No.": "2",
                "Description": "Item B",
                "Quantity": "20",
                "Unit": "pcs",
            },
            {
                "Date of Auction": "01/02/2023",
                "Auction List No.": "23",
                "Lot No.": "1",
                "Description": "Item C",
                "Quantity": "30",
                "Unit": "pcs",
            },
        ]

        with patch(
            "hkopenai.hk_misc_mcp_server.tools.auction.fetch_csv_from_url"
        ) as mock_fetch_csv_from_url:
            # Setup mock response for successful data fetching
            # Make it return mock_csv_data once, then empty list for subsequent calls
            mock_fetch_csv_from_url.side_effect = [mock_csv_data] + [[] for _ in range(23)]

            # Test filtering by date range
            result = _get_government_auction_data(2023, 1, 2023, 1, "EN")
            self.assertEqual(len(result), 2)
            self.assertEqual(result[0]["Description"], "Item A")
            self.assertEqual(result[1]["Description"], "Item B")

            # Reset mock for next test case
            mock_fetch_csv_from_url.reset_mock()
            mock_fetch_csv_from_url.side_effect = [[] for _ in range(24)] # All empty for non-matching dates

            # Test empty result for non-matching dates
            result = _get_government_auction_data(2024, 1, 2024, 1, "EN")
            self.assertEqual(len(result), 0)

            # Reset mock for next test case
            mock_fetch_csv_from_url.reset_mock()
            mock_fetch_csv_from_url.side_effect = [{"error": "CSV fetch failed"}] # Return error once

            # Test error handling when fetch_csv_from_url returns an error
            result = _get_government_auction_data(2023, 1, 2023, 1, "EN")
            self.assertEqual(result, {"type": "Error", "error": "CSV fetch failed"})

    def test_register_tool(self):
        """
        Test the registration of the get_government_auction_data tool.

        This test verifies that the register function correctly registers the tool
        with the FastMCP server and that the registered tool calls the underlying
        _get_government_auction_data function.
        """
        mock_mcp = MagicMock()

        # Call the register function
        register(mock_mcp)

        # Verify that mcp.tool was called with the correct description
        mock_mcp.tool.assert_called_once_with(
            description="Auction data of confiscated, used/surplus, and unclaimed stores from Government Logistics Department Hong Kong."
        )

        # Get the mock that represents the decorator returned by mcp.tool
        mock_decorator = mock_mcp.tool.return_value

        # Verify that the mock decorator was called once (i.e., the function was decorated)
        mock_decorator.assert_called_once()

        # The decorated function is the first argument of the first call to the mock_decorator
        decorated_function = mock_decorator.call_args[0][0]

        # Verify the name of the decorated function
        self.assertEqual(decorated_function.__name__, "get_government_auction_data")

        # Call the decorated function and verify it calls _get_government_auction_data
        with patch(
            "hkopenai.hk_misc_mcp_server.tools.auction._get_government_auction_data"
        ) as mock_get_government_auction_data:
            decorated_function(2023, 1, 2023, 1, "EN")
            mock_get_government_auction_data.assert_called_once_with(2023, 1, 2023, 1, "EN")