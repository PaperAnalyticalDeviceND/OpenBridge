"""
API tools for OpenBridge server.
Provides tools for interacting with the PAD API, including
OpenAPI spec parsing and dynamic tool generation.
"""

import os
import uuid
import json
import logging
import requests
import httpx
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path

from ..config import settings, auth_config

# Configure logger
logger = logging.getLogger(__name__)

def register_api_tools(mcp):
    """Register all API tools with the MCP server"""
    mcp.add_tool(fn=download_ontology, name="download_ontology")
    
    # Fetch OpenAPI spec and register dynamic tools
    spec = fetch_openapi_spec()
    if spec:
        register_openapi_endpoints_as_tools(mcp, spec)
    else:
        logger.error("Failed to fetch OpenAPI spec, dynamic tools not registered")


async def download_ontology() -> dict:
    """
    Download the PAD ontology file (ontology.ttl) from pad.crc.nd.edu.

    Returns:
        dict: A dictionary with the following structure:
            {
                "success": True/False,
                "data": <ontology file content as a string>,
                "error": <error message if any>,
                "description": "A summary of the action performed."
            }
    """
    ontology_url = f"{settings.server_base_url}/ontology/ontology.ttl"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                ontology_url, 
                timeout=settings.request_timeout,
                headers=auth_config.get_headers()
            )
            response.raise_for_status()
            ontology_content = response.text
        
        # Cache the ontology locally for future reference
        storage_path = Path(settings.filesystem_storage)
        if not storage_path.exists():
            storage_path.mkdir(parents=True, exist_ok=True)
        
        ontology_path = storage_path / "ontology.ttl"
        with open(ontology_path, "w", encoding="utf-8") as f:
            f.write(ontology_content)
        
        return {
            "success": True,
            "data": ontology_content,
            "error": "",
            "description": f"Successfully downloaded the PAD ontology file from {ontology_url} and cached at {ontology_path}."
        }
    except httpx.HTTPError as e:
        logger.exception(f"HTTP error downloading ontology: {e}")
        return {
            "success": False,
            "data": "",
            "error": f"HTTP error: {str(e)}",
            "description": f"Failed to download the PAD ontology file due to an HTTP error: {str(e)}"
        }
    except Exception as e:
        logger.exception(f"Error downloading ontology: {e}")
        return {
            "success": False,
            "data": "",
            "error": str(e),
            "description": f"Failed to download the PAD ontology file: {str(e)}"
        }


def fetch_openapi_spec(url: str = None) -> Optional[Dict[str, Any]]:
    """
    Fetches the OpenAPI JSON specification from the given URL.
    Returns the parsed JSON dict, or None on failure.
    """
    if url is None:
        url = settings.openapi_spec_url
        
    try:
        response = requests.get(
            url, 
            timeout=settings.request_timeout,
            headers=auth_config.get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch OpenAPI spec from {url}: {e}")
        return None


def normalize_tool_name(method: str, path: str) -> str:
    """
    Creates a function/tool name from HTTP method + path by
    removing slashes and braces, and converting spaces.
    Example: "GET /pets/{petId}" -> "get_pets_petId"
    """
    return (f"{method.lower()} {path}"
            .replace(" ", "_")
            .replace("/", "_")
            .replace("{", "")
            .replace("}", "")
            .replace("-", "_")
            .replace("__", "_")
            .lstrip("_"))


def should_register_endpoint(path: str, method: str, operation: Dict[str, Any]) -> bool:
    """
    Determine if an endpoint should be registered as a tool.
    
    Args:
        path: API endpoint path
        method: HTTP method (GET, POST, etc.)
        operation: OpenAPI operation object
        
    Returns:
        True if the endpoint should be registered, False otherwise
    """
    # Skip excluded patterns
    for pattern in settings.excluded_endpoint_patterns:
        if pattern in path.lower():
            logger.info(f"Skipping excluded endpoint: {method} {path} (matched pattern: {pattern})")
            return False
    
    # Skip endpoints without operationId (optional check)
    # if "operationId" not in operation:
    #     logger.warning(f"Skipping endpoint without operationId: {method} {path}")
    #     return False
    
    # Analyze responses to detect binary data endpoints
    responses = operation.get("responses", {})
    for response in responses.values():
        content = response.get("content", {})
        for mime_type in content.keys():
            # Skip binary responses that we don't handle specially
            if (mime_type.startswith("image/") or 
                mime_type.startswith("application/octet-stream") or
                mime_type.startswith("application/pdf")):
                if "download-image" not in path:  # We handle this one specially
                    logger.info(f"Skipping binary data endpoint: {method} {path} (mime type: {mime_type})")
                    return False
    
    return True


def make_api_request(url: str, method: str, params=None, json_data=None, timeout=None) -> Dict[str, Any]:
    """
    Make an authenticated HTTP request to the API with improved error handling.
    
    Args:
        url: The API endpoint URL
        method: HTTP method (GET, POST, etc.)
        params: Query parameters for GET requests
        json_data: JSON body for POST/PUT requests
        timeout: Request timeout in seconds
        
    Returns:
        Dict with response data or error information
    """
    if timeout is None:
        timeout = settings.request_timeout
        
    try:
        headers = auth_config.get_headers()
        
        response = requests.request(
            method=method.upper(),
            url=url,
            params=params if method.upper() == "GET" else None,
            json=json_data if method.upper() != "GET" else None,
            headers=headers,
            timeout=timeout
        )
        
        # Handle common HTTP status codes
        if response.status_code == 404:
            logger.error(f"Resource not found: {url}")
            return {
                "success": False,
                "error": f"Resource not found: {url}",
                "status_code": 404,
                "description": "The requested resource could not be found on the server."
            }
        elif response.status_code == 401:
            logger.error(f"Authentication required: {url}")
            return {
                "success": False,
                "error": "Authentication required",
                "status_code": 401,
                "description": "The request requires valid authentication credentials."
            }
        elif response.status_code == 403:
            logger.error(f"Access forbidden: {url}")
            return {
                "success": False,
                "error": "Access forbidden",
                "status_code": 403,
                "description": "You do not have permission to access this resource."
            }
        
        # Raise for other error status codes
        response.raise_for_status()
        
        # Check the Content-Type header
        content_type = response.headers.get("Content-Type", "").lower()
        
        # If it's an image or binary data, save it
        if content_type.startswith("image/") or content_type.startswith("application/octet-stream"):
            # Create storage path if needed
            storage_path = Path(settings.filesystem_storage)
            if not storage_path.exists():
                storage_path.mkdir(parents=True, exist_ok=True)
            
            # Determine file extension from content type
            ext = "bin"  # Default
            if content_type.startswith("image/"):
                ext = content_type.split("/")[1]
            
            # Generate filename
            filename = f"{uuid.uuid4()}.{ext}"
            full_path = storage_path / filename
            
            # Save the image bytes to a file
            with open(full_path, "wb") as file:
                file.write(response.content)
            
            return {
                "success": True,
                "filename": str(full_path),
                "path": str(full_path),
                "content_type": content_type,
                "description": f"The binary data has been saved to: {full_path}"
            }
        
        # Try to parse the body as JSON
        try:
            return response.json()
        except ValueError:
            # If it's not valid JSON, return the raw text
            return {
                "success": True,
                "data": response.text,
                "content_type": content_type,
                "description": "Response is not JSON data"
            }
            
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout for {url}")
        return {
            "success": False,
            "error": "Request timed out",
            "status_code": 408,
            "description": f"The request to {url} timed out after {timeout} seconds."
        }
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error for {url}")
        return {
            "success": False,
            "error": "Connection failed",
            "status_code": 503,
            "description": f"Could not connect to {url}. The server may be down or unreachable."
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for {url}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "status_code": 500,
            "description": f"Request failed: {str(e)}"
        }


def make_dynamic_tool_func(path: str, method: str, operation: Dict[str, Any]) -> Callable:
    """
    Create a dynamic tool function for a specific API endpoint.
    
    Args:
        path: API endpoint path
        method: HTTP method (GET, POST, etc.)
        operation: OpenAPI operation object
        
    Returns:
        Function that calls the API endpoint
    """
    def dynamic_tool_func(parameters: Optional[Dict[str, Any]] = {}) -> dict:
        """
        A dynamically-registered MCP tool that:
        - Takes a single dict of parameters.
        - Returns a Python dict from the HTTP JSON response, or a fallback structure if not valid JSON.
        """
        # Make a copy of parameters to avoid modifying the original
        params = parameters.copy() if parameters else {}
        
        # Build full URL with server base and API prefix
        final_url = f"{settings.server_base_url}{path}"
        
        # Replace path parameters like {petId} in /pets/{petId}
        for param in operation.get("parameters", []):
            if param.get("in") == "path":
                pname = param["name"]
                if pname in params:
                    value = str(params.pop(pname))
                    final_url = final_url.replace(f"{{{pname}}}", value)

        # Log URL for debugging
        logger.info(f"Calling API: {method.upper()} {final_url}")

        # If the endpoint is GET, treat any remaining keys as query params
        # Otherwise, treat them as JSON body
        method_upper = method.upper()
        
        return make_api_request(
            url=final_url,
            method=method_upper,
            params=params if method_upper == "GET" else None,
            json_data=params if method_upper != "GET" else None
        )
        
    return dynamic_tool_func


def register_openapi_endpoints_as_tools(mcp, spec: Dict[str, Any]) -> None:
    """
    Register API endpoints from an OpenAPI spec as MCP tools.
    
    Args:
        mcp: The MCP server instance
        spec: OpenAPI specification dictionary
    """
    registered_count = 0
    skipped_count = 0
    
    paths = spec.get("paths", {})
    for path, path_item in paths.items():
        if not path_item:
            continue
            
        for method, operation in path_item.items():
            method_lower = method.lower()
            if method_lower not in ["get", "post", "put", "delete", "patch"]:
                continue

            # Check if we should register this endpoint
            if not should_register_endpoint(path, method, operation):
                skipped_count += 1
                continue

            # Derive a function name from the endpoint
            tool_name = normalize_tool_name(method, path)
            
            # Build a docstring from the endpoint's summary/description
            summary = operation.get("summary", "")
            description = operation.get("description", "")
            docstring = f"{summary}\n\n{description}\n\n(This tool calls: {method.upper()} {path})"

            # Define the closure that makes the actual HTTP request
            dynamic_tool_func = make_dynamic_tool_func(path, method, operation)

            # Register the tool with MCP
            mcp.add_tool(fn=dynamic_tool_func, name=tool_name, description=docstring)
            registered_count += 1
            
            logger.info(f"Registered API tool: {tool_name}")
    
    logger.info(f"Registered {registered_count} API endpoints as tools (skipped {skipped_count})")
