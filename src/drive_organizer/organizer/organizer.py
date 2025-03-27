"""Main organizer functionality."""

import os
import asyncio
import tempfile
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from datetime import datetime
from pathlib import Path
import aiofiles
from loguru import logger
from ..recognition import ImageRecognizer, get_recognizer
from ..storage import StorageProvider, get_storage_provider


class DriveOrganizer:
    """Main organizer class for organizing images in cloud storage."""
    
    def __init__(
        self,
        recognition_provider: str = "gemini",
        storage_provider: str = "google_drive",
        config: Optional[Dict[str, Any]] = None,
        batch_size: int = 10,
        temp_dir: Optional[str] = None
    ):
        """
        Initialize the Drive Organizer.
        
        Args:
            recognition_provider: Name of the recognition provider to use
            storage_provider: Name of the storage provider to use
            config: Configuration dictionary
            batch_size: Number of images to process in a batch
            temp_dir: Directory to use for temporary files
        """
        config = config or {}
        
        # Initialize the image recognizer
        recognition_config = config.get("recognition", {})
        self.recognizer = get_recognizer(recognition_provider, recognition_config)
        
        # Initialize the storage provider
        storage_config = config.get("storage", {})
        self.storage = get_storage_provider(storage_provider, storage_config)
        
        # Configuration
        self.batch_size = batch_size
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.include_year = config.get("include_year", True)
        self.include_month = config.get("include_month", False)
        self.use_original_filenames = config.get("use_original_filenames", False)
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Track processed files
        self.processed_files: Set[str] = set()
        self.failed_files: Dict[str, str] = {}
    
    async def authenticate(self) -> bool:
        """
        Authenticate with the storage provider.
        
        Returns:
            True if authentication was successful
        """
        return await self.storage.authenticate()
    
    async def get_image_files(self, source_folder: str) -> List[Dict[str, Any]]:
        """
        Get all image files from a source folder.
        
        Args:
            source_folder: Path to the source folder
            
        Returns:
            List of file metadata dictionaries
        """
        # Define image file extensions
        image_extensions = [
            "jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "webp", "heic", "heif"
        ]
        
        # Get all files with image extensions
        return await self.storage.list_files(source_folder, image_extensions)
    
    async def process_batch(
        self,
        files: List[Dict[str, Any]],
        destination_folder: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[int, int]:
        """
        Process a batch of image files.
        
        Args:
            files: List of file metadata dictionaries
            destination_folder: Path to the destination folder
            progress_callback: Optional callback for reporting progress
            
        Returns:
            Tuple of (success_count, failure_count)
        """
        success_count = 0
        failure_count = 0
        
        # Download files to temporary directory
        temp_files = []
        for file_meta in files:
            try:
                file_id = file_meta["id"]
                file_name = file_meta["name"]
                temp_path = os.path.join(self.temp_dir, file_name)
                
                await self.storage.download_file(file_id, temp_path)
                temp_files.append((file_meta, temp_path))
            except Exception as e:
                logger.error(f"Failed to download file {file_meta['name']}: {e}")
                self.failed_files[file_meta["id"]] = str(e)
                failure_count += 1
                
                if progress_callback:
                    progress_callback(success_count, len(files))
        
        # Analyze files in a batch
        if temp_files:
            try:
                image_paths = [path for _, path in temp_files]
                results = await self.recognizer.analyze_image_batch(image_paths)
                
                # Process each file with its analysis result
                for i, ((file_meta, temp_path), (category, labels)) in enumerate(zip(temp_files, results)):
                    try:
                        # Skip files that have encountered errors during analysis
                        if category == "Error":
                            logger.error(f"Error analyzing file {file_meta['name']}")
                            self.failed_files[file_meta["id"]] = "Analysis error"
                            failure_count += 1
                            continue
                        
                        await self.organize_file(file_meta, temp_path, category, labels, destination_folder)
                        self.processed_files.add(file_meta["id"])
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Failed to organize file {file_meta['name']}: {e}")
                        self.failed_files[file_meta["id"]] = str(e)
                        failure_count += 1
                    
                    if progress_callback:
                        progress_callback(success_count + failure_count, len(files))
            
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                failure_count += len(temp_files)
        
        # Clean up temporary files
        for _, temp_path in temp_files:
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.error(f"Failed to remove temporary file {temp_path}: {e}")
        
        return success_count, failure_count
    
    async def organize_file(
        self,
        file_meta: Dict[str, Any],
        local_path: str,
        category: str,
        labels: List[str],
        destination_folder: str
    ) -> Dict[str, Any]:
        """
        Organize a single file.
        
        Args:
            file_meta: File metadata
            local_path: Path to the downloaded file
            category: Category detected by the recognizer
            labels: Labels detected by the recognizer
            destination_folder: Path to the destination folder
            
        Returns:
            Metadata of the organized file
        """
        # Determine the destination folder structure
        folder_path = destination_folder
        
        # Add category subfolder
        category_folder = f"{folder_path}/{category}"
        category_folder_meta = await self.storage.get_folder(category_folder, create_if_missing=True)
        
        # Add year/month folders if configured
        created_time = file_meta.get("createdTime", datetime.now().isoformat())
        try:
            created_date = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            created_date = datetime.now()
        
        current_folder = category_folder
        
        if self.include_year:
            year_folder = f"{category_folder}/{created_date.year}"
            year_folder_meta = await self.storage.get_folder(year_folder, create_if_missing=True)
            current_folder = year_folder
            
            if self.include_month:
                month_name = created_date.strftime("%B")  # Full month name
                month_folder = f"{year_folder}/{month_name}"
                month_folder_meta = await self.storage.get_folder(month_folder, create_if_missing=True)
                current_folder = month_folder
        
        # Determine the new file name
        if self.use_original_filenames:
            new_name = file_meta["name"]
        else:
            # Create a descriptive name based on labels and date
            label_part = "_".join(labels[:2]).lower().replace(" ", "_")
            date_part = created_date.strftime("%Y%m%d")
            file_ext = os.path.splitext(file_meta["name"])[1]
            new_name = f"{label_part}_{date_part}{file_ext}"
        
        # Upload the file to the destination folder
        result = await self.storage.upload_file(local_path, current_folder, new_name)
        
        return result
    
    async def organize_folder(
        self,
        source_folder: str,
        destination_folder: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[int, int]:
        """
        Organize all images in a folder.
        
        Args:
            source_folder: Path to the source folder
            destination_folder: Path to the destination folder
            progress_callback: Optional callback for reporting progress
            
        Returns:
            Tuple of (success_count, failure_count)
        """
        # Authenticate if needed
        if not await self.authenticate():
            raise ValueError("Authentication failed")
        
        # Get all image files in the source folder
        image_files = await self.get_image_files(source_folder)
        total_files = len(image_files)
        
        if not image_files:
            logger.warning(f"No image files found in {source_folder}")
            return 0, 0
        
        logger.info(f"Found {total_files} image files in {source_folder}")
        
        if progress_callback:
            progress_callback(0, total_files)
        
        # Process files in batches
        total_success = 0
        total_failure = 0
        
        for i in range(0, len(image_files), self.batch_size):
            batch = image_files[i:i + self.batch_size]
            success, failure = await self.process_batch(batch, destination_folder, progress_callback)
            total_success += success
            total_failure += failure
        
        logger.info(f"Organization complete. Successes: {total_success}, Failures: {total_failure}")
        
        return total_success, total_failure
    
    async def close(self):
        """Close connections and clean up resources."""
        await self.storage.close()
        if hasattr(self.recognizer, 'close'):
            await self.recognizer.close()
