"""
Image analysis tools for PAD cards.
Provides tools for analyzing PAD card images, including RGB value computation
and region analysis.
"""

import os
import logging
from typing import Dict, List, Any, Optional
import numpy as np
from PIL import Image as PILImage

# Configure logger
logger = logging.getLogger(__name__)

def register_analysis_tools(mcp):
    """Register all analysis tools with the MCP server"""
    mcp.add_tool(fn=compute_average_rgb, name="compute_average_rgb")
    mcp.add_tool(fn=analyze_image_regions, name="analyze_image_regions")


def compute_average_rgb(bbox: Optional[Dict[str, int]], image_path: str) -> dict:
    """
    Compute the average RGB values within a bounding box of an image.
    
    Args:
        bbox (dict): A dictionary specifying the bounding box with keys:
                     "x1", "y1" (top-left corner) and "x2", "y2" (bottom-right corner).
        image_path (str): The file system path to the image.
    
    Returns:
        dict: A dictionary with the following structure:
              {
                  "success": True/False,
                  "data": {
                      "avg_r": <average red>,
                      "avg_g": <average green>,
                      "avg_b": <average blue>
                  },
                  "error": "",          # Error message if any
                  "description": "Computed average RGB values for the specified bounding box."
              }
    """
    try:
        # Validate inputs
        if not os.path.exists(image_path):
            return {
                "success": False,
                "data": {},
                "error": f"Image path does not exist: {image_path}",
                "description": "Failed to locate the specified image file."
            }
        
        if not bbox or not all(key in bbox for key in ["x1", "y1", "x2", "y2"]):
            return {
                "success": False,
                "data": {},
                "error": "Bounding box must contain 'x1', 'y1', 'x2', and 'y2' keys.",
                "description": "Invalid bounding box specification."
            }
            
        # Open image and ensure it's in RGB mode
        try:
            img = PILImage.open(image_path)
            if img.mode != "RGB":
                img = img.convert("RGB")
        except Exception as e:
            return {
                "success": False,
                "data": {},
                "error": f"Failed to open image: {str(e)}",
                "description": "Could not open or process the image file."
            }
        
        # Extract bounding box coordinates
        x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]
        
        # Validate coordinates are within image bounds
        width, height = img.size
        if x1 < 0 or y1 < 0 or x2 > width or y2 > height or x1 >= x2 or y1 >= y2:
            return {
                "success": False,
                "data": {},
                "error": f"Invalid bounding box coordinates: {bbox} for image size {width}x{height}",
                "description": "Bounding box coordinates are outside image dimensions or invalid."
            }
        
        # Crop the image to the bounding box
        region = img.crop((x1, y1, x2, y2))
        
        # Convert the region to a numpy array and compute the average for each channel
        arr = np.array(region)
        avg_r = float(np.mean(arr[:, :, 0]))
        avg_g = float(np.mean(arr[:, :, 1]))
        avg_b = float(np.mean(arr[:, :, 2]))
        
        return {
            "success": True,
            "data": {
                "avg_r": avg_r,
                "avg_g": avg_g,
                "avg_b": avg_b,
                "region_size": {
                    "width": x2 - x1,
                    "height": y2 - y1
                }
            },
            "error": "",
            "description": f"Computed average RGB values for the specified bounding box ({x2-x1}x{y2-y1} pixels)."
        }
    except Exception as e:
        logger.exception("Error in compute_average_rgb")
        return {
            "success": False,
            "data": {},
            "error": str(e),
            "description": "Failed to compute average RGB values due to an error."
        }


def analyze_image_regions(image_path: str, regions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze multiple regions of an image and compute statistics for each region.
    
    Args:
        image_path (str): Path to the image file
        regions (List[Dict]): List of region definitions, each containing:
            - name: Region identifier
            - bbox: Bounding box with x1, y1, x2, y2 coordinates
            - metrics: List of metrics to compute ("avg", "std", "min", "max", "median")
    
    Returns:
        Dict with results for each region
    """
    try:
        # Validate image path
        if not os.path.exists(image_path):
            return {
                "success": False,
                "data": {},
                "error": f"Image path does not exist: {image_path}",
                "description": "Failed to locate the specified image file."
            }
        
        # Open and validate image
        try:
            img = PILImage.open(image_path)
            if img.mode != "RGB":
                img = img.convert("RGB")
        except Exception as e:
            return {
                "success": False,
                "data": {},
                "error": f"Failed to open image: {str(e)}",
                "description": "Could not open or process the image file."
            }
        
        img_array = np.array(img)
        results = {}
        
        # Process each region
        for i, region in enumerate(regions):
            # Default name if not provided
            name = region.get("name", f"region_{i+1}")
            bbox = region.get("bbox", {})
            metrics = region.get("metrics", ["avg"])
            
            # Validate metrics
            valid_metrics = ["avg", "std", "min", "max", "median", "mode"]
            metrics = [m for m in metrics if m in valid_metrics]
            
            # Validate bbox
            if not all(key in bbox for key in ["x1", "y1", "x2", "y2"]):
                results[name] = {
                    "error": "Invalid bounding box specification",
                    "valid": False
                }
                continue
            
            # Extract coordinates
            x1, y1 = bbox["x1"], bbox["y1"]
            x2, y2 = bbox["x2"], bbox["y2"]
            
            # Ensure coordinates are within image bounds
            width, height = img.size
            x1 = max(0, min(x1, width - 1))
            y1 = max(0, min(y1, height - 1))
            x2 = max(x1 + 1, min(x2, width))
            y2 = max(y1 + 1, min(y2, height))
            
            # Extract region
            try:
                region_array = img_array[y1:y2, x1:x2]
            except Exception as e:
                results[name] = {
                    "error": f"Failed to extract region: {str(e)}",
                    "valid": False,
                    "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                }
                continue
            
            # Initialize result dictionary for this region
            results[name] = {
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                "size": {"width": x2 - x1, "height": y2 - y1},
                "channels": {},
                "valid": True
            }
            
            # Compute metrics for each channel
            for channel_idx, channel_name in enumerate(["r", "g", "b"]):
                channel_data = region_array[:, :, channel_idx]
                channel_results = {}
                
                if "avg" in metrics:
                    channel_results["avg"] = float(np.mean(channel_data))
                if "std" in metrics:
                    channel_results["std"] = float(np.std(channel_data))
                if "min" in metrics:
                    channel_results["min"] = float(np.min(channel_data))
                if "max" in metrics:
                    channel_results["max"] = float(np.max(channel_data))
                if "median" in metrics:
                    channel_results["median"] = float(np.median(channel_data))
                if "mode" in metrics:
                    # Calculate mode (most common value)
                    values, counts = np.unique(channel_data, return_counts=True)
                    mode_idx = np.argmax(counts)
                    channel_results["mode"] = float(values[mode_idx])
                
                results[name]["channels"][channel_name] = channel_results
        
        return {
            "success": True,
            "data": results,
            "error": "",
            "description": f"Analyzed {len(results)} regions in the image."
        }
    except Exception as e:
        logger.exception("Error in analyze_image_regions")
        return {
            "success": False,
            "data": {},
            "error": str(e),
            "description": "Failed to analyze image regions due to an error."
        }
