"""Custom exceptions for the application."""

from fastapi import status

class DriveOrganizerException(Exception):
    """Base exception for Drive Organizer application."""

    def __init__(
        self,
        detail: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)

class AuthenticationError(DriveOrganizerException):
    """Exception for authentication errors."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail, status_code=status.HTTP_401_UNAUTHORIZED)

class ForbiddenError(DriveOrganizerException):
    """Exception for forbidden access."""

    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(detail, status_code=status.HTTP_403_FORBIDDEN)

class NotFoundError(DriveOrganizerException):
    """Exception for resource not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, status_code=status.HTTP_404_NOT_FOUND)

class ValidationError(DriveOrganizerException):
    """Exception for validation errors."""

    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class GoogleAPIError(DriveOrganizerException):
    """Exception for Google API errors."""

    def __init__(self, detail: str = "Google API error"):
        super().__init__(detail, status_code=status.HTTP_502_BAD_GATEWAY)

class GeminiAPIError(DriveOrganizerException):
    """Exception for Gemini API errors."""

    def __init__(self, detail: str = "Gemini API error"):
        super().__init__(detail, status_code=status.HTTP_502_BAD_GATEWAY)

class RedisError(DriveOrganizerException):
    """Exception for Redis errors."""

    def __init__(self, detail: str = "Redis error"):
        super().__init__(detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
