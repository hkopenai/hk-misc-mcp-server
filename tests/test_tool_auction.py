"""
Unit tests for auction data processing functions.

This module tests the functionality of various utility functions used for fetching
and processing auction data from the Government Logistics Department Hong Kong.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from io import StringIO
from hkopenai.hk_misc_mcp_server.tool_auction import (
    validate_language,
    create_date_range,
    fetch_csv_data,
    process_auction_row,
    _get_government_auction_data,
    register,
)


class TestAuctionData(unittest.TestCase):
    """
    Test class for auction data processing.

    This class contains test cases for validating language codes, creating date ranges,
    fetching CSV data, processing auction rows, and retrieving auction data.
    """

    def test_validate_language_valid(self):
        """
        Test validation of language codes with valid inputs.

        Verifies that the function correctly converts lowercase language codes to uppercase.
        """
        self.assertEqual(validate_language("en"), "EN")
        self.assertEqual(validate_language("tc"), "TC")
        self.assertEqual(validate_language("sc"), "SC")

    def test_validate_language_invalid(self):
        """
        Test validation of language codes with invalid input.

        Verifies that the function raises a ValueError for unsupported language codes.
        """
        with self.assertRaises(ValueError):
            validate_language("XX")

    def test_create_date_range(self):
        """
        Test creation of date range.

        Verifies that the function creates correct start and end datetime objects for the given year and month range.
        """
        start_date, end_date = create_date_range(2023, 1, 2023, 12)
        self.assertEqual(start_date, datetime(2023, 1, 1))
        self.assertEqual(end_date, datetime(2023, 12, 28))

    @patch("requests.get")
    def test_fetch_csv_data_success(self, mock_get):
        """
        Test fetching CSV data with a successful response.

        Verifies that the function returns a StringIO object with the correct content when the HTTP request succeeds.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"\xef\xbb\xbfSome CSV content"
        mock_get.return_value = mock_response

        result = fetch_csv_data("http://example.com/data.csv")
        self.assertIsInstance(result, StringIO)
        if result is not None:
            self.assertEqual(result.getvalue(), "Some CSV content")

    @patch("requests.get")
    def test_fetch_csv_data_404(self, mock_get):
        """
        Test fetching CSV data with a 404 response.

        Verifies that the function returns None when the HTTP request results in a 404 status code.
        """
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = fetch_csv_data("http://example.com/data.csv")
        self.assertIsNone(result)

    @patch("requests.get")
    def test_fetch_csv_data_other_status(self, mock_get):
        """
        Test fetching CSV data with a non-200, non-404 status code.

        Verifies that the function returns None when the HTTP request results in a status code other than 200 or 404.
        """
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = fetch_csv_data("http://example.com/data.csv")
        self.assertIsNone(result)

    @patch("requests.get")
    def test_fetch_csv_data_exception(self, mock_get):
        """
        Test fetching CSV data when an exception occurs.

        Verifies that the function returns None when an exception is raised during the HTTP request.
        """
        mock_get.side_effect = Exception("Network error")

        result = fetch_csv_data("http://example.com/data.csv")
        self.assertIsNone(result)

    def test_process_auction_row_missing_fields(self):
        """
        Test processing an auction row with missing required fields.

        Verifies that the function returns None when essential fields like Description or Quantity are missing.
        """
        row = {"Date of Auction": "21/03/2024"}
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 28)
        result = process_auction_row(row, start_date, end_date)
        self.assertIsNone(result)

    def test_process_auction_row_valid_date(self):
        """
        Test processing an auction row with a valid date within range.

        Verifies that the function correctly formats the date and returns a dictionary with auction details.
        """
        row = {
            "Date of Auction": "21/03/2024",
            "Auction List No.": "5/2024",
            "Lot No.": "C-401",
            "Description": "Watch (Brand: Casio)",
            "Quantity": "270",
            "Unit": "Nos.",
        }
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 28)
        result = process_auction_row(row, start_date, end_date)
        self.assertIsNotNone(result)
        if result is not None:
            self.assertEqual(result["Date of Auction"], "2024-03-21")
            self.assertEqual(result["Description"], "Watch (Brand: Casio)")
            self.assertEqual(result["Quantity"], "270")

    def test_process_auction_row_invalid_date(self):
        """
        Test processing an auction row with an invalid date format.

        Verifies that the function returns a dictionary with the original date string when the date cannot be parsed.
        """
        row = {
            "Date of Auction": "Invalid Date",
            "Auction List No.": "5/2024",
            "Lot No.": "C-401",
            "Description": "Watch (Brand: Casio)",
            "Quantity": "270",
            "Unit": "Nos.",
        }
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 28)
        result = process_auction_row(row, start_date, end_date)
        self.assertIsNotNone(result)
        if result is not None:
            self.assertEqual(result["Date of Auction"], "Invalid Date")
            self.assertEqual(result["Description"], "Watch (Brand: Casio)")
            self.assertEqual(result["Quantity"], "270")

    def test_process_auction_row_out_of_range(self):
        """
        Test processing an auction row with a date outside the specified range.

        Verifies that the function returns None when the auction date is outside the given date range.
        """
        row = {
            "Date of Auction": "21/03/2023",
            "Auction List No.": "5/2023",
            "Lot No.": "C-401",
            "Description": "Watch (Brand: Casio)",
            "Quantity": "270",
            "Unit": "Nos.",
        }
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 28)
        result = process_auction_row(row, start_date, end_date)
        self.assertIsNone(result)

    @patch("hkopenai.hk_misc_mcp_server.tool_auction.fetch_csv_data")
    def test_get_government_auction_data(self, mock_fetch):
        """
        Test retrieving auction data for a specified date range and language.

        Verifies that the function correctly fetches and processes auction data, returning only items within the date range.
        """
        mock_csv_content = StringIO(
            """Date of Auction,Auction List No.,Lot No.,Description,Quantity,Unit
21/03/2024,5/2024,C-401,Watch (Brand: Casio),270,Nos.
15/03/2023,5/2023,C-301,Tablet (Brand: Samsung),50,Nos."""
        )
        # Provide enough None responses to cover list numbers 24 to 1 for the year 2024
        mock_fetch.side_effect = [
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            mock_csv_content,
        ]

        result = _get_government_auction_data(2024, 1, 2024, 12, "EN")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Description"], "Watch (Brand: Casio)")
        self.assertEqual(result[0]["Quantity"], "270")

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
            "hkopenai.hk_misc_mcp_server.tool_auction._get_government_auction_data"
        ) as mock_get_government_auction_data:
            decorated_function(2023, 1, 2023, 12, "EN")
            mock_get_government_auction_data.assert_called_once_with(
                2023, 1, 2023, 12, "EN"
            )


if __name__ == "__main__":
    unittest.main()
