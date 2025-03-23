"""
Setup script for OpenBridge.
"""

from setuptools import setup, find_packages

setup(
    name="OpenBridge",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=[
        "mcp",
        "fastmcp",
        "pydantic",
        "pydantic-settings",
        "requests",
    ],
    entry_points={
        'console_scripts': [
            'openbridge=OpenBridge.server:run_server',
        ],
    },
)
