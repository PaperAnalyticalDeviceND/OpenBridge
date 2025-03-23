"""
Tests for the OpenBridge config module.
"""

import unittest
import tempfile
import os
from pathlib import Path

from OpenBridge.config import Settings


class TestConfig(unittest.TestCase):
    """Test the OpenBridge configuration module."""

    def test_settings_defaults(self):
        """Test that settings have the expected defaults."""
        settings = Settings()
        self.assertEqual(settings.server_base_url, "https://pad.crc.nd.edu")
        self.assertEqual(settings.api_prefix, "/api-ld/v3")
        self.assertTrue(settings.openapi_spec_url.endswith("/openapi.json"))
        self.assertIsNone(settings.api_key)
        self.assertIsNone(settings.auth_token)
        self.assertTrue(settings.filesystem_storage.endswith("storage"))
        self.assertEqual(settings.request_timeout, 30)
        self.assertEqual(settings.mcp_name, "paper_analytical_devices")
        self.assertIn("stream", settings.excluded_endpoint_patterns)
        self.assertIn("webpage", settings.excluded_endpoint_patterns)

    def test_storage_path_creation(self):
        """Test that the storage path is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tempdir:
            # Create a non-existent path
            storage_path = os.path.join(tempdir, "test_storage")
            
            # Verify it doesn't exist yet
            self.assertFalse(os.path.exists(storage_path))
            
            # Create settings with this path
            settings = Settings(filesystem_storage=storage_path)
            
            # Verify the path was created
            self.assertTrue(os.path.exists(storage_path))
            self.assertEqual(settings.filesystem_storage, storage_path)


if __name__ == "__main__":
    unittest.main()
