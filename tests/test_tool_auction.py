import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from io import StringIO
from hkopenai.hk_misc_mcp_server.tool_auction import (
    validate_language,
    create_date_range,
    fetch_csv_data,
    process_auction_row,
    get_auction_data
)

class TestAuctionData(unittest.TestCase):
    def test_validate_language_valid(self):
        self.assertEqual(validate_language('en'), 'EN')
        self.assertEqual(validate_language('tc'), 'TC')
        self.assertEqual(validate_language('sc'), 'SC')

    def test_validate_language_invalid(self):
        with self.assertRaises(ValueError):
            validate_language('XX')

    def test_create_date_range(self):
        start_date, end_date = create_date_range(2023, 1, 2023, 12)
        self.assertEqual(start_date, datetime(2023, 1, 1))
        self.assertEqual(end_date, datetime(2023, 12, 28))

    @patch('requests.get')
    def test_fetch_csv_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'\xef\xbb\xbfSome CSV content'
        mock_get.return_value = mock_response
        
        result = fetch_csv_data('http://example.com/data.csv')
        self.assertIsInstance(result, StringIO)
        if result is not None:
            self.assertEqual(result.getvalue(), 'Some CSV content')

    @patch('requests.get')
    def test_fetch_csv_data_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = fetch_csv_data('http://example.com/data.csv')
        self.assertIsNone(result)

    @patch('requests.get')
    def test_fetch_csv_data_other_status(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = fetch_csv_data('http://example.com/data.csv')
        self.assertIsNone(result)

    @patch('requests.get')
    def test_fetch_csv_data_exception(self, mock_get):
        mock_get.side_effect = Exception('Network error')
        
        result = fetch_csv_data('http://example.com/data.csv')
        self.assertIsNone(result)

    def test_process_auction_row_missing_fields(self):
        row = {'Date of Auction': '21/03/2024'}
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 28)
        result = process_auction_row(row, start_date, end_date)
        self.assertIsNone(result)

    def test_process_auction_row_valid_date(self):
        row = {
            'Date of Auction': '21/03/2024',
            'Auction List No.': '5/2024',
            'Lot No.': 'C-401',
            'Description': 'Watch (Brand: Casio)',
            'Quantity': '270',
            'Unit': 'Nos.'
        }
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 28)
        result = process_auction_row(row, start_date, end_date)
        self.assertIsNotNone(result)
        if result is not None:
            self.assertEqual(result['Date of Auction'], '2024-03-21')
            self.assertEqual(result['Description'], 'Watch (Brand: Casio)')
            self.assertEqual(result['Quantity'], '270')

    def test_process_auction_row_invalid_date(self):
        row = {
            'Date of Auction': 'Invalid Date',
            'Auction List No.': '5/2024',
            'Lot No.': 'C-401',
            'Description': 'Watch (Brand: Casio)',
            'Quantity': '270',
            'Unit': 'Nos.'
        }
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 28)
        result = process_auction_row(row, start_date, end_date)
        self.assertIsNotNone(result)
        if result is not None:
            self.assertEqual(result['Date of Auction'], 'Invalid Date')
            self.assertEqual(result['Description'], 'Watch (Brand: Casio)')
            self.assertEqual(result['Quantity'], '270')

    def test_process_auction_row_out_of_range(self):
        row = {
            'Date of Auction': '21/03/2023',
            'Auction List No.': '5/2023',
            'Lot No.': 'C-401',
            'Description': 'Watch (Brand: Casio)',
            'Quantity': '270',
            'Unit': 'Nos.'
        }
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 28)
        result = process_auction_row(row, start_date, end_date)
        self.assertIsNone(result)

    @patch('hkopenai.hk_misc_mcp_server.tool_auction.fetch_csv_data')
    def test_get_auction_data(self, mock_fetch):
        mock_csv_content = StringIO("""Date of Auction,Auction List No.,Lot No.,Description,Quantity,Unit
21/03/2024,5/2024,C-401,Watch (Brand: Casio),270,Nos.
15/03/2023,5/2023,C-301,Tablet (Brand: Samsung),50,Nos.""")
        # Provide enough None responses to cover list numbers 24 to 1 for the year 2024
        mock_fetch.side_effect = [
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, None, None, None, None, None, None, None,
            None, None, None, mock_csv_content
        ]
        
        result = get_auction_data(2024, 1, 2024, 12, 'EN')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['Description'], 'Watch (Brand: Casio)')
        self.assertEqual(result[0]['Quantity'], '270')

if __name__ == '__main__':
    unittest.main()
