# OpenBridge

OpenBridge is a Python package that provides a bridge API for PAD (Paper-based Analytical Device) storage and access. It serves as an interface between the PAD system and client applications, providing tools for data retrieval, analysis, and storage.

![Blank diagram (1)](https://github.com/user-attachments/assets/84a6d494-5b6e-45e3-89eb-410efcbd109c)
**Figure 1**: *System architecture of OpenBridge. A large language model (Claude Desktop) uses MCP to communicate with the OpenBridge server, which dynamically discovers and exposes API endpoints from OAS-compliant APIs as tools. JSON-LD responses provide semantic richness, improving interpretability for both agents and human users.*

## Features

- **API Integration**: Seamless integration with the PAD API
- **Analysis Tools**: Tools for analyzing PAD card images and data
- **File Handling**: Utilities for managing PAD-related files
- **Prompt Templates**: Predefined prompts for AI assistants working with PAD data

## Installation

```bash
# Install from source
pip install -e .
```

## Usage

### Running the server

```bash
# Run with stdio transport (default)
openbridge

# Run with http transport
openbridge http
```

### Using with fastmcp for development

```bash
# Debug mode
fastmcp dev OpenBridge_server.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
