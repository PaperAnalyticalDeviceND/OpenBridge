"""
Main server module for the OpenBridge server.
Initializes the MCP server, registers tools and prompts,
and handles server startup.
"""

import os
import sys
import logging
from typing import Optional

# MCP imports
from mcp.server.fastmcp import FastMCP
from fastmcp.prompts import Prompt  # Import the Prompt class

# Local imports
from .config import settings, logger
from . import prompts
from .tools import analysis, files, api


def register_prompt_dynamically(mcp, fn, name=None, description=None):
    """
    Dynamically register a prompt with the MCP server using the Prompt class.
    
    Args:
        mcp: The MCP server instance
        fn: The function to register as a prompt
        name: Optional name for the prompt (defaults to function name)
        description: Optional description (defaults to function docstring)
    
    Returns:
        The registered prompt
    """
    try:
        # Use the function name if name is not provided
        prompt_name = name or fn.__name__
        
        # Create a Prompt instance from the function
        prompt = Prompt.from_function(fn, name=prompt_name, description=description)
        
        # Register the prompt with the MCP server
        mcp.add_prompt(prompt)
        
        # Store with name for future reference if needed
        setattr(mcp, f"prompt_{prompt_name}", prompt)
        
        logger.info(f"Dynamically registered prompt: {prompt_name}")
        return prompt
    except Exception as e:
        # If anything goes wrong, fall back to the decorator approach
        logger.warning(f"Error registering prompt dynamically: {e}, falling back to decorator approach for {fn.__name__}")
        decorated = mcp.prompt()(fn)
        setattr(mcp, f"prompt_{name or fn.__name__}", decorated)
        return decorated

def initialize_mcp() -> FastMCP:
    """
    Initialize the MCP server with all tools and prompts.
    
    Returns:
        Configured FastMCP instance
    """
    # Create MCP instance
    mcp = FastMCP(settings.mcp_name)
    
    # Register prompts
    register_prompts(mcp)
    
    # Register tools
    register_tools(mcp)
    
    return mcp


def register_prompts(mcp: FastMCP) -> None:
    """
    Register all prompts with the MCP server.
    
    Args:
        mcp: The MCP server instance
    """
    # Use direct decorators without function calls
    for name, func in [
        ("system_introduction", prompts.pad_system_introduction),
        ("tool_reminders", prompts.pad_tool_reminders),
        ("analyze_pad_card", prompts.analyze_pad_card),
        ("project_overview", prompts.project_overview),
        ("new_user_introduction", prompts.new_user_introduction),
        ("debug_card_analysis", prompts.debug_card_analysis),
        ("recommend_analysis_improvements", prompts.recommend_analysis_improvements),
    ]:
        # Register the prompt with MCP
        decorated = mcp.prompt()(func)
        
        # Store with name for future reference if needed
        setattr(mcp, f"prompt_{name}", decorated)
    
    # Dynamically register compare_pad_cards using the Prompt class
    register_prompt_dynamically(mcp, prompts.compare_pad_cards)
    
    logger.info("Registered all prompts")


def register_tools(mcp: FastMCP) -> None:
    """
    Register all tools with the MCP server.
    
    Args:
        mcp: The MCP server instance
    """
    # Register analysis tools
    analysis.register_analysis_tools(mcp)
    
    # Register file tools
    files.register_file_tools(mcp)
    
    # Register API tools (including dynamic ones from OpenAPI spec)
    api.register_api_tools(mcp)
    
    logger.info("Registered all tools")


def run_server(transport: str = "stdio") -> None:
    """
    Start the MCP server with the specified transport.
    
    Args:
        transport: Transport to use ("stdio", "http", etc.)
    """
    # Initialize MCP
    mcp = initialize_mcp()
    
    # Log startup information
    logger.info(f"Starting OpenBridge server with {transport} transport")
    logger.info(f"Server name: {settings.mcp_name}")
    logger.info(f"API base URL: {settings.server_base_url}")
    logger.info(f"Storage directory: {settings.filesystem_storage}")
    
    # Start server with specified transport
    mcp.run(transport=transport)


if __name__ == "__main__":
    """
    Entry point for running the server directly.
    """
    # Default to stdio transport
    transport = "stdio"
    
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        transport = sys.argv[1]
        
    # Run server
    run_server(transport)
