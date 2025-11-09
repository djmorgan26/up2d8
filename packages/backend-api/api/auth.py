from auth import User, get_current_user
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.get("/me")
async def get_user_profile(user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.

    This route is protected and requires a valid Entra ID token.
    """
    return {
        "user_id": user.sub,
        "name": user.name,
        "email": user.email,
        "username": user.preferred_username,
        "oid": user.oid,
    }


@router.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    """
    Example protected route that requires authentication.

    Use this pattern for any route that needs authentication:
        async def my_route(user: User = Depends(get_current_user)):
    """
    return {
        "message": f"Hello {user.name or user.email or 'User'}!",
        "authenticated": True,
        "user_id": user.sub,
    }
