"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..dependencies import get_current_user
from ..config import get_settings
from ..models.auth import TokenResponse, UserResponse

settings = get_settings()
router = APIRouter()

# TODO: Implement server-side token exchange if needed, or remove if handled client-side
@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatibility endpoint - not implemented."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Direct password authentication not supported. Use Firebase Authentication."
    )

@router.get("/me", response_model=UserResponse)
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """Get authenticated user information."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "picture": current_user.get("picture", ""),
    }

# TODO: Implement token refresh endpoint if needed, or remove if handled client-side
@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Token refresh - not implemented."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token refresh should be handled by the Firebase client SDK."
    )
