from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check for duplicate email
    result = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with email '{user_in.email}' already exists",
        )

    # Validate role
    if user_in.role not in ("ADMIN", "ANALYST", "VIEWER"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid role '{user_in.role}'. Must be ADMIN, ANALYST, or VIEWER.",
        )

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT access token",
)
async def login(
    login_in: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == login_in.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated",
        )

    access_token = create_access_token(
        subject=user.id,
        role=user.role,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
