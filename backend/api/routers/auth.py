"""Authentication router for user signup, login, and token management."""

from datetime import datetime
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse

from api.db.cosmos_db import get_cosmos_client, CosmosCollections
from api.models.user import (
    UserCreate,
    UserLogin,
    TokenRefresh,
    AuthResponse,
    TokenResponse,
    UserResponse,
)
from api.utils.auth import (
    hash_password,
    verify_password,
    create_token_pair,
    decode_token,
    get_current_user,
)
from api.utils.oauth import oauth, get_google_user_info, validate_oauth_config


router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """
    Register a new user account.

    Creates a new user with hashed password and default preferences.

    Args:
        user_data: User registration data (email, password, full_name)

    Returns:
        AuthResponse with user data and authentication tokens

    Raises:
        HTTPException 400: If email already exists
        HTTPException 422: If validation fails
    """
    cosmos = get_cosmos_client()
    users_collection = cosmos.get_collection(CosmosCollections.USERS)

    # Check if user already exists
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user document
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "password_hash": hashed_password,
        "full_name": user_data.full_name,
        "tier": "free",
        "status": "active",
        "onboarding_completed": False,
        "oauth_provider": None,
        "oauth_id": None,
        "created_at": datetime.utcnow(),
        "last_login_at": datetime.utcnow(),
    }

    # Create default preferences
    preferences_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "subscribed_companies": [],
        "subscribed_industries": [],
        "digest_frequency": "daily",
        "delivery_time": "08:00:00",
        "timezone": "America/New_York",
        "delivery_days": [1, 2, 3, 4, 5],  # Mon-Fri
        "email_format": "html",
        "article_count_per_digest": 7,
        "summary_style": "standard",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    try:
        # Insert user
        users_collection.insert_one(user_doc)

        # Insert preferences
        prefs_collection = cosmos.get_collection(CosmosCollections.USER_PREFERENCES)
        prefs_collection.insert_one(preferences_doc)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

    # Create tokens
    tokens = create_token_pair(user_id)

    # Return response
    return AuthResponse(
        user=UserResponse(
            id=user_id,
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            tier=user_doc["tier"],
            status=user_doc["status"],
            onboarding_completed=user_doc["onboarding_completed"],
            created_at=user_doc["created_at"],
            last_login_at=user_doc["last_login_at"],
        ),
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    """
    Authenticate user and return tokens.

    Args:
        credentials: User login credentials (email, password)

    Returns:
        AuthResponse with user data and authentication tokens

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 403: If account is suspended
    """
    cosmos = get_cosmos_client()
    users_collection = cosmos.get_collection(CosmosCollections.USERS)

    # Find user by email
    user_doc = users_collection.find_one({"email": credentials.email})

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, user_doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check account status
    if user_doc.get("status") == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended. Please contact support."
        )

    if user_doc.get("status") == "deleted":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deleted"
        )

    # Update last login
    users_collection.update_one(
        {"id": user_doc["id"]},
        {"$set": {"last_login_at": datetime.utcnow()}}
    )
    user_doc["last_login_at"] = datetime.utcnow()

    # Create tokens
    tokens = create_token_pair(user_doc["id"])

    return AuthResponse(
        user=UserResponse(
            id=user_doc["id"],
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            tier=user_doc.get("tier", "free"),
            status=user_doc.get("status", "active"),
            onboarding_completed=user_doc.get("onboarding_completed", False),
            created_at=user_doc.get("created_at"),
            last_login_at=user_doc.get("last_login_at"),
        ),
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh):
    """
    Refresh access token using refresh token.

    Args:
        token_data: Refresh token

    Returns:
        TokenResponse with new access token

    Raises:
        HTTPException 401: If refresh token is invalid or expired
    """
    # Decode and validate refresh token
    payload = decode_token(token_data.refresh_token)

    # Verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new token pair
    tokens = create_token_pair(user_id)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: dict = Depends(get_current_user),
):
    """
    Logout user (invalidate tokens).

    Note: With JWT tokens, true invalidation requires a token blacklist.
    For MVP, this is a placeholder that confirms authentication.
    Client should delete tokens on their side.

    Args:
        current_user: Current authenticated user

    Returns:
        204 No Content
    """
    # TODO: Implement token blacklist in Redis for production
    # For now, this endpoint serves to validate the token
    # Client is responsible for deleting tokens
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's information.

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse with user data
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        tier=current_user.get("tier", "free"),
        status=current_user.get("status", "active"),
        onboarding_completed=current_user.get("onboarding_completed", False),
        created_at=current_user.get("created_at"),
        last_login_at=current_user.get("last_login_at"),
    )


@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth login flow.

    Returns:
        Redirect to Google OAuth consent screen
    """
    if not validate_oauth_config():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured. Please contact support."
        )

    # Generate redirect URI
    redirect_uri = request.url_for('google_callback')

    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request):
    """
    Handle Google OAuth callback.

    Creates or logs in user based on Google account info.

    Returns:
        Redirect to frontend with tokens in URL params (or error page)
    """
    try:
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)

        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            # Fallback: fetch user info manually
            user_info = await get_google_user_info(token['access_token'])

        if not user_info or not user_info.get('email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user information from Google"
            )

        email = user_info['email']
        full_name = user_info.get('name', email.split('@')[0])
        google_id = user_info.get('sub')  # Google user ID

        cosmos = get_cosmos_client()
        users_collection = cosmos.get_collection(CosmosCollections.USERS)

        # Check if user exists
        existing_user = users_collection.find_one({"email": email})

        if existing_user:
            # User exists - log them in
            user_id = existing_user["id"]

            # Update OAuth info if not set
            if not existing_user.get("oauth_provider"):
                users_collection.update_one(
                    {"id": user_id},
                    {"$set": {
                        "oauth_provider": "google",
                        "oauth_id": google_id,
                        "last_login_at": datetime.utcnow()
                    }}
                )
            else:
                # Just update last login
                users_collection.update_one(
                    {"id": user_id},
                    {"$set": {"last_login_at": datetime.utcnow()}}
                )
        else:
            # Create new user
            user_id = str(uuid.uuid4())
            user_doc = {
                "id": user_id,
                "email": email,
                "password_hash": "",  # No password for OAuth users
                "full_name": full_name,
                "tier": "free",
                "status": "active",
                "onboarding_completed": False,
                "oauth_provider": "google",
                "oauth_id": google_id,
                "created_at": datetime.utcnow(),
                "last_login_at": datetime.utcnow(),
            }

            # Create default preferences
            preferences_doc = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "subscribed_companies": [],
                "subscribed_industries": [],
                "digest_frequency": "daily",
                "delivery_time": "08:00:00",
                "timezone": "America/New_York",
                "delivery_days": [1, 2, 3, 4, 5],
                "email_format": "html",
                "article_count_per_digest": 7,
                "summary_style": "standard",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            try:
                users_collection.insert_one(user_doc)
                prefs_collection = cosmos.get_collection(CosmosCollections.USER_PREFERENCES)
                prefs_collection.insert_one(preferences_doc)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create user: {str(e)}"
                )

        # Create tokens
        tokens = create_token_pair(user_id)

        # Redirect to frontend with tokens
        # For now, return JSON (frontend can handle this)
        return JSONResponse({
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "expires_in": tokens["expires_in"],
        })

    except Exception as e:
        print(f"Google OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )
