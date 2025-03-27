"""Factory for creating storage providers."""

from typing import Dict, Any, Optional
from loguru import logger
from .base import StorageProvider
from .google_drive import GoogleDriveProvider


def get_storage_provider(provider: str = "google_drive", config: Optional[Dict[str, Any]] = None) -> StorageProvider:
    """
    Factory function to create the appropriate storage provider.
    
    Args:
        provider: The name of the storage provider to use (currently only "google_drive")
        config: Optional configuration dictionary for the provider
    
    Returns:
        An instance of the requested StorageProvider
    
    Raises:
        ValueError: If the requested provider is not supported
    """
    if provider.lower() == "google_drive":
        logger.info("Creating Google Drive storage provider")
        return GoogleDriveProvider(config)
    else:
        raise ValueError(f"Unsupported storage provider: {provider}. " 
                         f"Supported providers are: 'google_drive'")
