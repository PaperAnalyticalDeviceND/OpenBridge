"""
Main entry point for running the OpenBridge package directly.

This allows the package to be run using:
`python -m OpenBridge [transport]`
"""

import sys
from .server import run_server

if __name__ == "__main__":
    # Default to stdio transport
    transport = "stdio"
    
    # Parse command line arguments if provided
    if len(sys.argv) > 1:
        transport = sys.argv[1]
    
    # Run the server
    run_server(transport)
