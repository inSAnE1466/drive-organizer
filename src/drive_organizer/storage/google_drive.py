"""Google Drive storage provider."""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional, BinaryIO, Tuple, AsyncIterator
from pathlib import Path
import aiohttp
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from loguru import logger
from .base import StorageProvider


class GoogleDriveProvider(StorageProvider):
    """Storage provider for Google Drive."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Google Drive provider.
        
        Args:
            config: Optional configuration dictionary
        """
        self.client_id = os.environ.get("GOOGLE_CLIENT_ID")
        self.client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8080")
        self.token_path = os.environ.get("GOOGLE_TOKEN_PATH", "token.json")
        self.credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
        
        # SCOPES for Google Drive API
        self.scopes = ['https://www.googleapis.com/auth/drive']
        
        if config:
            self.client_id = config.get("client_id", self.client_id)
            self.client_secret = config.get("client_secret", self.client_secret)
            self.redirect_uri = config.get("redirect_uri", self.redirect_uri)
            self.token_path = config.get("token_path", self.token_path)
            self.credentials_path = config.get("credentials_path", self.credentials_path)
        
        self.credentials = None
        self.service = None
        
    async def authenticate(self) -> bool:
        """
        Authenticate with Google Drive.
        
        Returns:
            True if authentication is successful, False otherwise
        """
        # Check if we already have a token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'r') as token:
                self.credentials = Credentials.from_authorized_user_info(
                    json.load(token), self.scopes)
        
        # If there are no valid credentials, let's get some
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: self.credentials.refresh(Request()))
            else:
                if not os.path.exists(self.credentials_path):
                    # If no credentials file exists, create one with client ID and secret
                    if self.client_id and self.client_secret:
                        credentials_data = {
                            "installed": {
                                "client_id": self.client_id,
                                "client_secret": self.client_secret,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                "redirect_uris": [self.redirect_uri, "urn:ietf:wg:oauth:2.0:oob"]
                            }
                        }
                        with open(self.credentials_path, 'w') as credentials_file:
                            json.dump(credentials_data, credentials_file)
                    else:
                        logger.error("No credentials file found and no client ID/secret provided.")
                        return False
                
                # Run the OAuth flow to get a token
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes)
                
                loop = asyncio.get_event_loop()
                self.credentials = await loop.run_in_executor(
                    None, lambda: flow.run_local_server(port=0))
                
                # Save the credentials for the next run
                with open(self.token_path, 'w') as token:
                    token.write(self.credentials.to_json())
        
        # Build the service
        loop = asyncio.get_event_loop()
        self.service = await loop.run_in_executor(
            None, lambda: build('drive', 'v3', credentials=self.credentials))
        
        return self.service is not None
    
    async def list_files(self, folder_path: str, file_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List files in a Google Drive folder.
        
        Args:
            folder_path: Path to the folder (can be a name or an ID)
            file_types: Optional list of file extensions to filter by
            
        Returns:
            List of file metadata dictionaries
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        # Get the folder ID if a path was provided
        folder_id = folder_path
        if not folder_path.startswith("folder:"):
            folder = await self.get_folder(folder_path)
            if folder:
                folder_id = folder["id"]
            else:
                return []
        
        # Build the query
        query = f"'{folder_id}' in parents and trashed = false"
        
        if file_types:
            type_conditions = []
            for file_type in file_types:
                if not file_type.startswith("."):
                    file_type = f".{file_type}"
                type_conditions.append(f"name contains '{file_type}'")
            
            if type_conditions:
                query += f" and ({' or '.join(type_conditions)})"
        
        loop = asyncio.get_event_loop()
        
        # Execute the query
        result = await loop.run_in_executor(
            None,
            lambda: self.service.files().list(
                q=query,
                fields="files(id, name, mimeType, createdTime, modifiedTime, parents, size)",
                pageSize=1000
            ).execute()
        )
        
        return result.get('files', [])
    
    async def download_file(self, file_id: str, destination: str) -> str:
        """
        Download a file from Google Drive.
        
        Args:
            file_id: ID of the file to download
            destination: Local path to save the file
            
        Returns:
            Path to the downloaded file
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
        
        loop = asyncio.get_event_loop()
        
        # Get file metadata to determine MIME type
        file_metadata = await loop.run_in_executor(
            None,
            lambda: self.service.files().get(fileId=file_id, fields="name,mimeType").execute()
        )
        
        # Handle Google Docs and other Google formats
        mime_type = file_metadata.get('mimeType', '')
        is_google_doc = mime_type.startswith('application/vnd.google-apps')
        
        if is_google_doc and mime_type != 'application/vnd.google-apps.folder':
            # Map Google Docs formats to exportable MIME types
            export_formats = {
                'application/vnd.google-apps.document': 'application/pdf',
                'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'application/vnd.google-apps.drawing': 'image/png',
            }
            
            export_mime = export_formats.get(mime_type, 'application/pdf')
            
            # Export the file
            request = self.service.files().export_media(fileId=file_id, mimeType=export_mime)
        else:
            # Regular download for non-Google formats
            request = self.service.files().get_media(fileId=file_id)
        
        # Download the file
        with open(destination, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = await loop.run_in_executor(None, downloader.next_chunk)
        
        return destination
    
    async def upload_file(self, source: str, destination_folder: str, new_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a file to Google Drive.
        
        Args:
            source: Local path of the file to upload
            destination_folder: Path or ID of the destination folder
            new_name: Optional new name for the file
            
        Returns:
            Metadata of the uploaded file
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        # Get folder ID if a path was provided
        folder_id = destination_folder
        if not destination_folder.startswith("folder:"):
            folder = await self.get_folder(destination_folder, create_if_missing=True)
            if folder:
                folder_id = folder["id"]
            else:
                raise ValueError(f"Destination folder not found: {destination_folder}")
        
        # Prepare file metadata
        file_name = new_name if new_name else os.path.basename(source)
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        # Prepare media
        media = MediaFileUpload(
            source,
            resumable=True
        )
        
        loop = asyncio.get_event_loop()
        
        # Execute the upload
        file = await loop.run_in_executor(
            None,
            lambda: self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,mimeType,createdTime,modifiedTime,parents,size'
            ).execute()
        )
        
        return file
    
    async def create_folder(self, folder_name: str, parent_folder: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new folder in Google Drive.
        
        Args:
            folder_name: Name of the folder to create
            parent_folder: Optional parent folder ID or path
            
        Returns:
            Metadata of the created folder
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        # Get parent folder ID if a path was provided
        parent_id = parent_folder
        if parent_folder and not parent_folder.startswith("folder:"):
            parent = await self.get_folder(parent_folder, create_if_missing=True)
            if parent:
                parent_id = parent["id"]
        
        # Prepare folder metadata
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            folder_metadata['parents'] = [parent_id]
        
        loop = asyncio.get_event_loop()
        
        # Create the folder
        folder = await loop.run_in_executor(
            None,
            lambda: self.service.files().create(
                body=folder_metadata,
                fields='id,name,mimeType,createdTime,modifiedTime,parents'
            ).execute()
        )
        
        return folder
    
    async def get_folder(self, folder_path: str, create_if_missing: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get a folder by path, optionally creating it if it doesn't exist.
        
        Args:
            folder_path: Path to the folder (e.g., "My Drive/Photos/Vacation")
            create_if_missing: Whether to create the folder if it doesn't exist
            
        Returns:
            Folder metadata or None if not found and not created
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        # Split the path into components
        if folder_path == "root" or folder_path == "My Drive":
            # Special case for root folder
            loop = asyncio.get_event_loop()
            root = await loop.run_in_executor(
                None,
                lambda: self.service.files().get(fileId='root').execute()
            )
            return root
        
        parts = folder_path.rstrip('/').split('/')
        
        # Start with the root folder
        current_folder_id = 'root'
        current_path = []
        
        for part in parts:
            current_path.append(part)
            part_path = '/'.join(current_path)
            
            # Search for the folder
            query = f"name = '{part}' and '{current_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            
            loop = asyncio.get_event_loop()
            
            result = await loop.run_in_executor(
                None,
                lambda: self.service.files().list(
                    q=query,
                    fields="files(id, name, mimeType, parents)",
                    pageSize=1
                ).execute()
            )
            
            folders = result.get('files', [])
            
            if not folders:
                # Folder not found
                if create_if_missing:
                    # Create the folder
                    new_folder = await self.create_folder(part, current_folder_id)
                    current_folder_id = new_folder['id']
                else:
                    logger.warning(f"Folder not found: {part_path}")
                    return None
            else:
                # Use the first matching folder
                current_folder_id = folders[0]['id']
        
        # Get the final folder details
        loop = asyncio.get_event_loop()
        folder = await loop.run_in_executor(
            None,
            lambda: self.service.files().get(
                fileId=current_folder_id,
                fields='id,name,mimeType,createdTime,modifiedTime,parents'
            ).execute()
        )
        
        return folder
    
    async def stream_download(self, file_id: str) -> AsyncIterator[bytes]:
        """
        Stream download a file from Google Drive.
        
        Args:
            file_id: ID of the file to download
            
        Yields:
            Chunks of the file content
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        loop = asyncio.get_event_loop()
        
        # Get file metadata
        file_metadata = await loop.run_in_executor(
            None,
            lambda: self.service.files().get(fileId=file_id, fields="name,mimeType").execute()
        )
        
        # Handle Google Docs and other Google formats
        mime_type = file_metadata.get('mimeType', '')
        is_google_doc = mime_type.startswith('application/vnd.google-apps')
        
        if is_google_doc and mime_type != 'application/vnd.google-apps.folder':
            # For Google Docs, we can't use streaming download
            # Instead, we need to export to a standard format
            raise ValueError("Streaming download not supported for Google Docs formats")
        
        # Get the download URL
        request = self.service.files().get_media(fileId=file_id)
        download_url = request.uri
        
        # Create a session
        async with aiohttp.ClientSession() as session:
            # Stream the file content
            async with session.get(
                download_url,
                headers={"Authorization": f"Bearer {self.credentials.token}"}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"Failed to download file: {error_text}")
                
                # Yield chunks of the file
                chunk_size = 1024 * 1024  # 1 MB chunks
                async for chunk in response.content.iter_chunked(chunk_size):
                    yield chunk
    
    async def close(self) -> None:
        """Close any open connections."""
        # Nothing specific to close for Google Drive API
        pass
