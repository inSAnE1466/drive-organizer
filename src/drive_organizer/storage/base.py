"""Base class for storage providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, BinaryIO, Tuple, AsyncIterator
from pathlib import Path


class StorageProvider(ABC):
    """Abstract base class for storage providers."""
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the storage provider.
        
        Returns:
            True if authentication is successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_files(self, folder_path: str, file_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List files in a folder.
        
        Args:
            folder_path: Path to the folder
            file_types: Optional list of file extensions to filter by
            
        Returns:
            List of file metadata dictionaries
        """
        pass
    
    @abstractmethod
    async def download_file(self, file_id: str, destination: str) -> str:
        """
        Download a file to a local destination.
        
        Args:
            file_id: ID of the file to download
            destination: Local path to save the file
            
        Returns:
            Path to the downloaded file
        """
        pass
    
    @abstractmethod
    async def upload_file(self, source: str, destination_folder: str, new_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to a destination folder.
        
        Args:
            source: Local path of the file to upload
            destination_folder: Path to the destination folder
            new_name: Optional new name for the file
            
        Returns:
            Metadata of the uploaded file
        """
        pass
    
    @abstractmethod
    async def create_folder(self, folder_name: str, parent_folder: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new folder.
        
        Args:
            folder_name: Name of the folder to create
            parent_folder: Optional parent folder ID
            
        Returns:
            Metadata of the created folder
        """
        pass
    
    @abstractmethod
    async def get_folder(self, folder_path: str, create_if_missing: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a folder by path, optionally creating it if it doesn't exist.
        
        Args:
            folder_path: Path to the folder
            create_if_missing: Whether to create the folder if it doesn't exist
            
        Returns:
            Folder metadata or None if not found and not created
        """
        pass
    
    @abstractmethod
    async def stream_download(self, file_id: str) -> AsyncIterator[bytes]:
        """
        Stream download a file.
        
        Args:
            file_id: ID of the file to download
            
        Yields:
            Chunks of the file content
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close any open connections or resources."""
        pass
