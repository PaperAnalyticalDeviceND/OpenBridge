#!/bin/bash
# Simple installation script for OpenBridge

# Create a virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

# Install the package in development mode
echo "Installing OpenBridge in development mode..."
pip install -e .

# Install test dependencies
echo "Installing test dependencies..."
pip install pytest pytest-cov

echo "OpenBridge installation complete!"
echo "You can now run the server with: openbridge"
echo "Or use it with fastmcp: fastmcp dev OpenBridge_server.py"
