"""Authentication models."""

from pydantic import BaseModel, EmailStr, Field

class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Expiration in seconds")
    refresh_token: str

class UserResponse(BaseModel):
    """User response model."""

    id: str
    email: EmailStr
    name: str
    picture: str = ""
