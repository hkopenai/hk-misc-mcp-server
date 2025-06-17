import unittest
from unittest.mock import patch, Mock
from hkopenai.hk_misc_mcp_server.app import create_mcp_server

class TestApp(unittest.TestCase):
    @patch('hkopenai.hk_misc_mcp_server.app.FastMCP')
    @patch('hkopenai.hk_misc_mcp_server.tool_auction.get_auction_data')
    def test_create_mcp_server(self, mock_tool_auction, mock_fastmcp):
        # Setup mocks
        mock_server = unittest.mock.Mock()
        
        # Track decorator calls and capture decorated functions
        decorator_calls = []
        decorated_funcs = {}
        
        def tool_decorator(description=None):
            # First call: @tool(description=...)
            decorator_calls.append(((), {'description': description}))
            
            def decorator(f):
                # Second call: decorator(function)
                nonlocal decorated_funcs
                decorated_funcs[f.__name__] = f
                return f
                
            return decorator
            
        mock_server.tool = tool_decorator
        mock_fastmcp.return_value = mock_server
        mock_tool_auction.return_value = [
            {
                'Date of Auction': '21/3/2024',
                'Auction List No.': '5/2024',
                'Lot No.': 'C-401',
                'Description': 'Watch (Brand: Casio, Model: AQ-S810W)',
                'Quantity': '270',
                'Unit': 'Nos.'
            }
        ]

        # Test server creation
        server = create_mcp_server()

        # Verify server creation
        mock_fastmcp.assert_called_once()
        self.assertEqual(server, mock_server)

        # Verify tools were decorated
        self.assertIn('get_auction_data', decorated_funcs)
        
        # Test the actual decorated function for auction data
        auction_func = decorated_funcs.get('get_auction_data')
        if auction_func:
            result = auction_func(2024, 3, 2024, 3, 'EN')
            mock_tool_auction.assert_called_once_with(2024, 3, 2024, 3, 'EN')
            self.assertEqual(result, mock_tool_auction.return_value)

if __name__ == "__main__":
    unittest.main()
