"""Dependency injection for the API."""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer

from .services.redis import get_redis_client

from .config import get_settings

settings = get_settings()

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    auto_error=False
)

async def get_current_user(
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    """Get the current authenticated user from Bearer token."""
    # Extract token from Authorization header if not provided via OAuth2
    if authorization and authorization.startswith("Bearer ") and not token:
        token = authorization.replace("Bearer ", "")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: Implement Firebase auth token verification
    return {
        "id": "mock-user-id",
        "email": "user@example.com",
        "name": "Test User",
    }

async def get_redis():
    """Get Redis client connection."""
    redis_client = await get_redis_client()
    yield redis_client
