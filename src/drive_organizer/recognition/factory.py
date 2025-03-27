"""Factory for creating image recognizers."""

from typing import Dict, Any, Optional
from loguru import logger
from .base import ImageRecognizer
from .aws import AWSRecognizer
from .gemini import GeminiRecognizer


def get_recognizer(provider: str = "gemini", config: Optional[Dict[str, Any]] = None) -> ImageRecognizer:
    """
    Factory function to create the appropriate image recognizer.
    
    Args:
        provider: The name of the recognition provider to use ("aws" or "gemini")
        config: Optional configuration dictionary for the recognizer
    
    Returns:
        An instance of the requested ImageRecognizer
    
    Raises:
        ValueError: If the requested provider is not supported
    """
    if provider.lower() == "aws":
        logger.info("Creating AWS Rekognition recognizer")
        return AWSRecognizer(config)
    
    elif provider.lower() == "gemini":
        logger.info("Creating Google Gemini recognizer")
        return GeminiRecognizer(config)
    
    else:
        raise ValueError(f"Unsupported image recognition provider: {provider}. " 
                         f"Supported providers are: 'aws', 'gemini'")
