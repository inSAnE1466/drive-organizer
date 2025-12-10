"""Custom middleware for the application."""

import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from .config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log details."""
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request details
        logger.info(
            f"{request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Processing time: {process_time:.4f}s"
        )
        
        return response

class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for Firebase authentication."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # TODO: Initialize Firebase Admin SDK
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and verify Firebase token if present."""
        # Skip authentication for non-API routes or auth-related routes
        path = request.url.path
        if not path.startswith(f"{settings.API_V1_STR}") or path.startswith(f"{settings.API_V1_STR}/auth"):
            return await call_next(request)
            
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")

            # TODO: Implement Firebase token verification
            logger.info(f"Got bearer token: {token[:10]}...")
            request.state.user = {
                "id": "mock-user-id",
                "email": "user@example.com",
                "name": "Test User",
            }
        
        return await call_next(request)
