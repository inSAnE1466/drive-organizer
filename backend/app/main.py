"""Main application module for Drive Organizer backend."""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .middleware import LoggingMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .utils.exceptions import DriveOrganizerException

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create application
settings = get_settings()

app = FastAPI(
    title="Drive Organizer",
    description="AI-powered image organization for Google Drive",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    debug=settings.DEBUG
)

# Add middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
# TODO: Add FirebaseAuthMiddleware

# Global exception handler
@app.exception_handler(DriveOrganizerException)
async def drive_organizer_exception_handler(request: Request, exc: DriveOrganizerException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Import and include routers
from .api import auth

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
# TODO: Add routers for drive, analysis, organization, stats

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Drive Organizer API is running"}

@app.get(f"{settings.API_V1_STR}")
async def api_root():
    """API root endpoint."""
    return {
        "name": "Drive Organizer API",
        "version": "0.1.0",
        "docs": f"{settings.API_V1_STR}/docs"
    }
