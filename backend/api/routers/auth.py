"""Authentication router for user signup, login, and token management."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.db.session import get_db
from api.db.models import User, UserPreference
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
    authenticate_user,
    create_token_pair,
    decode_token,
    get_current_user,
)


router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Creates a new user with hashed password and default preferences.

    Args:
        user_data: User registration data (email, password, full_name)
        db: Database session

    Returns:
        AuthResponse with user data and authentication tokens

    Raises:
        HTTPException 400: If email already exists
        HTTPException 422: If validation fails
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        tier="free",
        status="active",
        onboarding_completed=False,
    )

    try:
        db.add(new_user)
        db.flush()  # Flush to get the user ID

        # Create default preferences for the user
        user_preferences = UserPreference(
            user_id=new_user.id,
            subscribed_companies=[],
            subscribed_industries=[],
            digest_frequency="daily",
            delivery_time="08:00:00",
            timezone="America/New_York",
            delivery_days=[1, 2, 3, 4, 5],  # Mon-Fri
            email_format="html",
            article_count_per_digest=7,
            summary_style="standard",
        )
        db.add(user_preferences)
        db.commit()
        db.refresh(new_user)

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        ) from e

    # Update last login
    new_user.last_login_at = datetime.utcnow()
    db.commit()

    # Create tokens
    tokens = create_token_pair(new_user.id)

    # Return response
    return AuthResponse(
        user=UserResponse.model_validate(new_user),
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
    )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return tokens.

    Args:
        credentials: User login credentials (email, password)
        db: Database session

    Returns:
        AuthResponse with user data and authentication tokens

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 403: If account is suspended
    """
    # Authenticate user
    user = authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check account status
    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended. Please contact support."
        )

    if user.status == "deleted":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deleted"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create tokens
    tokens = create_token_pair(user.id)

    return AuthResponse(
        user=UserResponse.model_validate(user),
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
    current_user: User = Depends(get_current_user),
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
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.

    Args:
        current_user: Current authenticated user

    Returns:
        UserResponse with user data
    """
    return UserResponse.model_validate(current_user)
