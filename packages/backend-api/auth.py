import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from pydantic import BaseModel

# Load environment variables
TENANT_ID = os.getenv("ENTRA_TENANT_ID")
CLIENT_ID = os.getenv("ENTRA_CLIENT_ID")
AUDIENCE = os.getenv("ENTRA_AUDIENCE", f"api://{CLIENT_ID}")

if not TENANT_ID or not CLIENT_ID:
    raise ValueError("ENTRA_TENANT_ID and ENTRA_CLIENT_ID must be set in environment variables")

# Configure Azure AD authentication
azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=CLIENT_ID,
    tenant_id=TENANT_ID,
    scopes={
        f"{AUDIENCE}/access_as_user": "Access the API as a user",
    },
    allow_guest_users=True,
)


class User(BaseModel):
    """Authenticated user model"""

    sub: str  # Subject (user ID)
    name: str | None = None
    email: str | None = None
    preferred_username: str | None = None
    oid: str | None = None  # Object ID in Azure AD
    iss: str | None = None  # Issuer (OAuth provider)


async def get_current_user(auth: HTTPAuthorizationCredentials = Depends(azure_scheme)) -> User:
    """
    Dependency to get the current authenticated user.

    Usage in route:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.sub, "email": user.email}
    """
    try:
        # azure_scheme already validates the token
        # The auth object contains the validated claims
        return User(
            sub=auth.get("sub", ""),
            name=auth.get("name"),
            email=auth.get("email"),
            preferred_username=auth.get("preferred_username"),
            oid=auth.get("oid"),
            iss=auth.get("iss"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional: Simple bearer token scheme for manual validation
http_bearer = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> dict:
    """
    Alternative: Manual token verification without fastapi-azure-auth.
    Use this if you need custom validation logic.
    """
    token = credentials.credentials

    # This would require manual JWT validation using python-jose
    # For now, use get_current_user instead
    raise NotImplementedError("Use get_current_user dependency instead")
