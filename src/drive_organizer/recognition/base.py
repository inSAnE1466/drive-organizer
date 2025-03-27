"""Base class for image recognition services."""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
import os
from pathlib import Path


class ImageRecognizer(ABC):
    """Abstract base class for image recognition services."""

    @abstractmethod
    async def analyze_image(self, image_path: str) -> Tuple[str, List[str]]:
        """
        Analyze an image and return its category and labels.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple containing (category, list of labels)
        """
        pass
    
    @abstractmethod
    async def analyze_image_batch(self, image_paths: List[str]) -> List[Tuple[str, List[str]]]:
        """
        Analyze a batch of images and return categories and labels for each.

        Args:
            image_paths: List of paths to image files

        Returns:
            List of tuples containing (category, list of labels) for each image
        """
        pass
    
    @abstractmethod
    def get_supported_categories(self) -> Dict[str, List[str]]:
        """
        Get the mapping of supported categories to their keywords.

        Returns:
            Dictionary mapping category names to lists of keywords
        """
        pass
    
    @staticmethod
    def load_categories_from_config(config_path: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Load categories from a configuration file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dictionary mapping category names to lists of keywords
        """
        # Default categories if no config is provided
        default_categories = {
            'Landscapes': ['mountain', 'ocean', 'sunset', 'beach', 'forest', 'river', 'waterfall', 'lake'],
            'People': ['person', 'face', 'group', 'crowd', 'portrait', 'selfie', 'family'],
            'Food': ['meal', 'dish', 'restaurant', 'cooking', 'dinner', 'lunch', 'breakfast', 'food'],
            'Animals': ['dog', 'cat', 'bird', 'pet', 'wildlife', 'zoo', 'farm', 'animal'],
            'Buildings': ['building', 'architecture', 'house', 'skyscraper', 'monument', 'church', 'temple'],
            'Transportation': ['car', 'vehicle', 'bicycle', 'motorcycle', 'bus', 'train', 'airplane', 'boat'],
            'Events': ['wedding', 'party', 'concert', 'festival', 'ceremony', 'celebration', 'conference'],
            'Documents': ['document', 'text', 'paper', 'receipt', 'certificate', 'letter', 'contract'],
            'Screenshots': ['screenshot', 'screen', 'display', 'monitor', 'computer', 'interface', 'app'],
            'Other': []
        }
        
        # TODO: Implement config file parsing
        return default_categories
