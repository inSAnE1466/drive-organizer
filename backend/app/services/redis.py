"""Redis service for data storage and retrieval."""

import json
from typing import Dict, List, Any, Optional, Set
import logging
import redis.asyncio as redis
from ..config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# TODO: Move to dependency injection instead of global state
_redis_client = None

async def get_redis_client():
    """Get or create Redis client."""
    global _redis_client

    if _redis_client is None:
        # TODO: Add proper connection pool management and retry logic
        _redis_client = redis.from_url(
            settings.REDIS_URI,
            encoding="utf-8",
            decode_responses=True
        )
        await _redis_client.ping()
        logger.info("Connected to Redis")

    return _redis_client

async def store_image_metadata(image_id: str, metadata: Dict[str, Any], redis_client) -> bool:
    """Store image metadata in Redis."""
    try:
        tags = metadata.get("tags", [])
        if isinstance(tags, list):
            metadata["tags"] = json.dumps(tags)
        elif isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except json.JSONDecodeError:
                tags = []

        await redis_client.hset(f"image:{image_id}", mapping=metadata)
        
        # Store the image ID in a set of all images
        await redis_client.sadd("all_images", image_id)
        
        # If user_id is provided, add to user's images
        if "user_id" in metadata:
            await redis_client.sadd(f"user:{metadata['user_id']}:images", image_id)
        
        # If tags are provided, index them
        for tag in tags:
            if tag:
                # Add image to tag set
                await redis_client.sadd(f"tag:{tag}", image_id)
                # Add tag to image's tags set
                await redis_client.sadd(f"image:{image_id}:tags", tag)
        
        # If category is provided, index it
        if "category" in metadata and metadata["category"]:
            category = metadata["category"]
            await redis_client.sadd(f"category:{category}", image_id)
        
        return True
    except Exception as e:
        logger.error(f"Failed to store image metadata: {e}")
        return False

async def get_image_metadata(image_id: str, redis_client) -> Optional[Dict[str, Any]]:
    """Get image metadata from Redis."""
    try:
        # Get metadata
        metadata = await redis_client.hgetall(f"image:{image_id}")
        
        if not metadata:
            return None
        
        tags = await redis_client.smembers(f"image:{image_id}:tags")
        if tags:
            metadata["tags"] = list(tags)
        elif "tags" in metadata:
            try:
                metadata["tags"] = json.loads(metadata["tags"])
            except json.JSONDecodeError:
                metadata["tags"] = []

        return metadata
    except Exception as e:
        logger.error(f"Failed to get image metadata: {e}")
        return None
