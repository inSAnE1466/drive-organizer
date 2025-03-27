"""AWS Rekognition implementation of image recognition."""

import os
import boto3
from typing import Dict, List, Tuple, Optional, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from .base import ImageRecognizer


class AWSRecognizer(ImageRecognizer):
    """Image recognition using AWS Rekognition."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AWS Rekognition client.
        
        Args:
            config: Configuration dictionary with AWS settings
        """
        self.access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        self.secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.region = os.environ.get("AWS_REGION", "us-west-2")
        
        if config:
            self.access_key = config.get("aws_access_key_id", self.access_key)
            self.secret_key = config.get("aws_secret_access_key", self.secret_key)
            self.region = config.get("aws_region", self.region)
            
        # Verify credentials are available
        if not self.access_key or not self.secret_key:
            logger.warning("AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        
        self.client = boto3.client(
            'rekognition',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
        
        self.categories = self.load_categories_from_config()
        self._executor = ThreadPoolExecutor(max_workers=os.cpu_count())
    
    def get_supported_categories(self) -> Dict[str, List[str]]:
        """Get the mapping of supported categories to their keywords."""
        return self.categories
    
    def _analyze_single_image(self, image_path: str) -> Tuple[str, List[str]]:
        """
        Analyze a single image using AWS Rekognition.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple containing (category, list of labels)
        """
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()
            
            response = self.client.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=20
            )
            
            labels = [label['Name'].lower() for label in response.get('Labels', [])]
            
            # Determine category based on labels
            category = "Other"
            for cat_name, keywords in self.categories.items():
                if any(keyword in labels for keyword in keywords):
                    category = cat_name
                    break
            
            return category, labels
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return "Error", []
    
    async def analyze_image(self, image_path: str) -> Tuple[str, List[str]]:
        """
        Analyze an image and return its category and labels.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple containing (category, list of labels)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self._analyze_single_image, image_path)
    
    async def analyze_image_batch(self, image_paths: List[str]) -> List[Tuple[str, List[str]]]:
        """
        Analyze a batch of images in parallel.
        
        Args:
            image_paths: List of paths to image files
            
        Returns:
            List of tuples containing (category, list of labels) for each image
        """
        tasks = [self.analyze_image(path) for path in image_paths]
        return await asyncio.gather(*tasks)
