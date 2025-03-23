"""
Tests for the OpenBridge tools modules.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import io
import tempfile
from pathlib import Path

from OpenBridge.tools.analysis import compute_average_rgb, analyze_image_regions
from OpenBridge.tools.files import load_image, save_image


class TestAnalysisTools(unittest.TestCase):
    """Test the OpenBridge analysis tools."""
    
    @patch('OpenBridge.tools.analysis.PILImage')
    @patch('OpenBridge.tools.analysis.np')
    @patch('os.path.exists')
    def test_compute_average_rgb(self, mock_exists, mock_np, mock_pil):
        """Test the compute_average_rgb function."""
        # Setup mocks
        mock_exists.return_value = True
        mock_img = MagicMock()
        mock_img.size = (100, 100)
        mock_pil.open.return_value = mock_img
        mock_img.mode = "RGB"
        
        mock_array = MagicMock()
        mock_np.array.return_value = mock_array
        mock_np.mean.side_effect = [10.5, 20.5, 30.5]
        
        # Call the function
        bbox = {"x1": 10, "y1": 10, "x2": 50, "y2": 50}
        result = compute_average_rgb(bbox, "test_image.png")
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["avg_r"], 10.5)
        self.assertEqual(result["data"]["avg_g"], 20.5)
        self.assertEqual(result["data"]["avg_b"], 30.5)
        self.assertEqual(result["data"]["region_size"]["width"], 40)
        self.assertEqual(result["data"]["region_size"]["height"], 40)
        
        # Verify the image was processed correctly
        mock_exists.assert_called_once_with("test_image.png")
        mock_pil.open.assert_called_once_with("test_image.png")
        mock_img.crop.assert_called_once_with((10, 10, 50, 50))


class TestFileTools(unittest.TestCase):
    """Test the OpenBridge file tools."""
    
    def test_save_image(self):
        """Test the save_image function with actual file operations."""
        with tempfile.TemporaryDirectory() as tempdir:
            # Setup test environment
            os.environ["OPENBRIDGE_FILESYSTEM_STORAGE"] = tempdir
            
            # Create a simple test image
            test_image_data = b"Test image data"
            
            # Call the function
            result = save_image(test_image_data, "test.png")
            
            # Clean up environment
            del os.environ["OPENBRIDGE_FILESYSTEM_STORAGE"]


if __name__ == "__main__":
    unittest.main()
