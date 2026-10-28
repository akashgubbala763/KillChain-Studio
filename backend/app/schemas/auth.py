from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: str = Field(..., min_length=5, max_length=255, examples=["analyst@soc.local"])
    password: str = Field(..., min_length=8, max_length=128, examples=["SecurePassword123!"])
    full_name: str = Field(..., min_length=1, max_length=100, examples=["Jane Doe"])
    role: str = Field(default="ANALYST", pattern="^(ADMIN|ANALYST|VIEWER)$")


class UserLogin(BaseModel):
    """Schema for login request."""
    email: str = Field(..., examples=["analyst@soc.local"])
    password: str = Field(..., examples=["SecurePassword123!"])


class UserResponse(BaseModel):
    """Schema for returning user information (no password)."""
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token response after successful login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenPayload(BaseModel):
    """Decoded JWT payload."""
    sub: str
    role: str
    exp: Optional[int] = None
