#!/usr/bin/env python
"""
Debug script for OpenBridge server.
This script initializes the OpenBridge server without running it,
allowing it to be used with 'fastmcp dev OpenBridge_server.py'
"""

from OpenBridge.server import initialize_mcp
from OpenBridge.config import settings, logger

# Initialize MCP server but don't run it
mcp = initialize_mcp()

# Log information
logger.info(f"OpenBridge server initialized for debugging")
logger.info(f"Server name: {settings.mcp_name}")
logger.info(f"API base URL: {settings.server_base_url}")
logger.info(f"Storage directory: {settings.filesystem_storage}")

# This makes the 'mcp' variable available when imported with fastmcp dev
# The script will not run the server automatically
