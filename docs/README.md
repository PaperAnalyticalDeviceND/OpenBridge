# OpenBridge Documentation

This directory contains documentation for the OpenBridge package.

## Overview

OpenBridge provides a bridge API for PAD (Paper-based Analytical Device) storage and access. It serves as an interface between the PAD system and client applications, providing tools for data retrieval, analysis, and storage.

## Contents

- **API Reference**: Documentation for the API exposed by OpenBridge
- **Usage Examples**: Examples of how to use OpenBridge in different scenarios
- **Configuration**: Details on configuring OpenBridge for different environments

## Getting Started

To get started with OpenBridge, see the main README.md file in the project root.

## Building Documentation

Documentation is built using Sphinx. To build the documentation:

```bash
# Install Sphinx and required extensions
pip install sphinx sphinx-rtd-theme

# Build HTML documentation
cd docs
make html
```

The built documentation will be available in the `_build/html` directory.
