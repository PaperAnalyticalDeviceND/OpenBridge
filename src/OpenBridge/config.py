"""
Configuration module for the OpenBridge server.
Provides centralized configuration with validation using Pydantic.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="openbridge.log",
    filemode="a"
)

# Create a module-level logger
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings with validation"""
    # API configuration
    server_base_url: str = Field(
        default="https://pad.crc.nd.edu",
        description="Base URL for the PAD API server"
    )
    api_prefix: str = Field(
        default="/api-ld/v3",
        description="Prefix path for API endpoints"
    )
    openapi_spec_url: str = Field(
        default="https://pad.crc.nd.edu/api-ld/v3/openapi.json",
        description="URL for the OpenAPI specification"
    )
    
    # Authentication
    api_key: Optional[str] = Field(
        default=None,
        description="API key for PAD API authentication"
    )
    auth_token: Optional[str] = Field(
        default=None,
        description="Authentication token for PAD API"
    )
    
    # File storage
    filesystem_storage: str = Field(
        default="./storage",
        description="Directory for storing downloaded files"
    )
    
    # HTTP client settings
    request_timeout: int = Field(
        default=30,
        description="Timeout for HTTP requests in seconds",
        ge=1,
        le=300
    )
    
    # MCP settings
    mcp_name: str = Field(
        default="paper_analytical_devices",
        description="Name for the MCP server"
    )
    
    # Excluded endpoint patterns (endpoints that should not be registered as tools)
    excluded_endpoint_patterns: list = Field(
        default=["stream", "webpage"],
        description="Patterns to exclude from tool registration"
    )
    
    @field_validator("filesystem_storage")
    def validate_storage_path(cls, v, info):
        """Ensure the storage path exists or can be created"""
        path = Path(v).expanduser().resolve()
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created storage directory: {path}")
            except Exception as e:
                logger.warning(f"Could not create storage directory: {e}")
        return str(path)
    
    model_config = {
        "env_file": ".env",
        "env_prefix": "OPENBRIDGE_"
    }


class AuthConfig:
    """Authentication configuration and utilities"""
    def __init__(self, settings: Settings):
        self.api_key = settings.api_key
        self.auth_token = settings.auth_token
    
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers based on available credentials"""
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers


# Create global instances
settings = Settings()
auth_config = AuthConfig(settings)

# Log configuration on initialization
logger.info(f"Server base URL: {settings.server_base_url}")
logger.info(f"OpenAPI spec URL: {settings.openapi_spec_url}")
logger.info(f"Storage directory: {settings.filesystem_storage}")
logger.info(f"Authentication configured: {bool(settings.api_key or settings.auth_token)}")
