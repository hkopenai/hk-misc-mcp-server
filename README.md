# Hong Kong Government Data MCP Server

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/hkopenai/hk-misc-mcp-server)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is an MCP server that provides access to various Hong Kong government data through a FastMCP interface.

## Features

### Government Auction Data
- Get auction data of confiscated, used/surplus, and unclaimed stores from Government Logistics Department

## Data Source

- Auction data from Government Logistics Department

## Examples

* Get latest auction data for confiscated and surplus items in Hong Kong

## Setup

1. Clone this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python server.py
   ```

### Running Options

- Default stdio mode: `python server.py`
- SSE mode (port 8000): `python server.py --sse`

## Cline Integration

To connect this MCP server to Cline using stdio:

1. Add this configuration to your Cline MCP settings (cline_mcp_settings.json):
```json
{
  "hk-misc": {
    "disabled": false,
    "timeout": 3,
    "type": "stdio",
    "command": "uvx",
    "args": [
      "hkopenai.hk-misc-mcp-server"
    ]
  }
}
```

## Testing

Tests are available in the `tests/` directory. Run with:
```bash
pytest
```
