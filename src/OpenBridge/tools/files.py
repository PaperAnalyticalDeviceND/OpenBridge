"""
File handling tools for OpenBridge server.
Provides tools for loading, saving, and managing files.
"""

import os
import io
import uuid
import logging
from typing import Optional
from pathlib import Path
from PIL import Image as PILImage
from mcp.server.fastmcp import Image

from ..config import settings

# Configure logger
logger = logging.getLogger(__name__)

def register_file_tools(mcp):
    """Register all file handling tools with the MCP server"""
    mcp.add_tool(fn=load_image, name="load_image")
    mcp.add_tool(fn=save_image, name="save_image")


def load_image(path: str, resize_width: Optional[int] = None, maintain_aspect_ratio: bool = True) -> Image:
    """
    Load an image from disk with optional resizing.
    
    Args:
        path: Path to the image file
        resize_width: Optional width to resize the image to (in pixels)
        maintain_aspect_ratio: Whether to maintain the aspect ratio when resizing (default: True)
        
    Returns:
        The loaded (and optionally resized) image
    """
    try:
        # Validate path
        if not os.path.exists(path):
            raise ValueError(f"Image file not found: {path}")
        
        # First, load the image using PIL
        img = PILImage.open(path)
        
        # Resize if specified
        if resize_width is not None and resize_width > 0:
            if maintain_aspect_ratio:
                # Calculate height to maintain aspect ratio
                aspect_ratio = img.height / img.width
                resize_height = int(resize_width * aspect_ratio)
            else:
                # Use original height if not maintaining aspect ratio
                resize_height = img.height
                
            img = img.resize((resize_width, resize_height), PILImage.LANCZOS)
            
        # Convert to bytes for FastMCP
        buffer = io.BytesIO()
        img.save(buffer, format=img.format or "PNG")
        buffer.seek(0)
        
        # Return the image for FastMCP
        return Image(data=buffer.getvalue())
        
    except Exception as e:
        logger.exception(f"Error loading image: {path}")
        raise ValueError(f"Error loading or resizing image: {str(e)}")


def save_image(image_data: bytes, filename: Optional[str] = None, format: str = "PNG") -> dict:
    """
    Safely save image data to filesystem.
    
    Args:
        image_data: Raw image data bytes
        filename: Optional filename to use (if None, a UUID will be generated)
        format: Image format to save as (default: PNG)
        
    Returns:
        Dict with success status and path information
    """
    try:
        # Validate parameters
        if not image_data:
            return {
                "success": False,
                "error": "No image data provided",
                "description": "Image data is empty or None"
            }
        
        # Create storage path if needed
        storage_path = Path(settings.filesystem_storage)
        if not storage_path.exists():
            storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created storage directory: {storage_path}")
        
        # Generate safe filename or use provided one
        if not filename:
            filename = f"{uuid.uuid4()}.{format.lower()}"
        
        # Ensure filename doesn't contain path traversal
        safe_filename = os.path.basename(filename)
        
        # Create full path
        full_path = storage_path / safe_filename
        
        # Load image data to validate it's actually an image
        try:
            img = PILImage.open(io.BytesIO(image_data))
            
            # Save to file
            img.save(full_path, format=format)
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid image data: {str(e)}",
                "description": "Could not process or save the provided image data"
            }
        
        return {
            "success": True,
            "filename": safe_filename,
            "path": str(full_path),
            "description": f"Image successfully saved to {full_path}"
        }
        
    except Exception as e:
        logger.exception("Error saving image")
        return {
            "success": False,
            "error": str(e),
            "description": "Failed to save image due to an error"
        }
