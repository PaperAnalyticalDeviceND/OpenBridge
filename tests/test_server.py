"""
Tests for the OpenBridge server module.
"""

import unittest
from unittest.mock import patch, MagicMock

from OpenBridge.server import initialize_mcp, register_tools


class TestServer(unittest.TestCase):
    """Test the OpenBridge server module."""

    @patch('OpenBridge.server.FastMCP')
    def test_initialize_mcp(self, mock_fastmcp):
        """Test that initialize_mcp creates and configures a FastMCP instance."""
        # Create a mock FastMCP instance
        mock_mcp = MagicMock()
        mock_fastmcp.return_value = mock_mcp
        
        # Call the function being tested
        result = initialize_mcp()
        
        # Verify FastMCP was created with the correct name
        mock_fastmcp.assert_called_once()
        
        # Verify the result is the mocked FastMCP instance
        self.assertEqual(result, mock_mcp)
        
        # Verify that register_prompts and register_tools were called
        mock_mcp.prompt.assert_called()
        
        # Verify the result is properly configured
        self.assertEqual(result, mock_mcp)

    @patch('OpenBridge.tools.analysis.register_analysis_tools')
    @patch('OpenBridge.tools.files.register_file_tools')
    @patch('OpenBridge.tools.api.register_api_tools')
    def test_register_tools(self, mock_api, mock_files, mock_analysis):
        """Test that register_tools calls all the tool registration functions."""
        # Create a mock FastMCP instance
        mock_mcp = MagicMock()
        
        # Call the function being tested
        register_tools(mock_mcp)
        
        # Verify that all registration functions were called with the mcp instance
        mock_analysis.assert_called_once_with(mock_mcp)
        mock_files.assert_called_once_with(mock_mcp)
        mock_api.assert_called_once_with(mock_mcp)


if __name__ == "__main__":
    unittest.main()
