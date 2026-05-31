from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Payload for POST /api/v1/auth/register"""
    name: str = Field(..., min_length=2, max_length=100, examples=["Jane Doe"])
    email: EmailStr = Field(..., examples=["jane@example.com"])
    password: str = Field(..., min_length=8, max_length=128, examples=["Str0ng!Pass"])

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be blank or whitespace.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v


class LoginRequest(BaseModel):
    """Payload for POST /api/v1/auth/login"""
    email: EmailStr = Field(..., examples=["jane@example.com"])
    password: str = Field(..., examples=["Str0ng!Pass"])


class TokenResponse(BaseModel):
    """Returned after successful login or registration."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token lifetime in seconds")


class UserResponse(BaseModel):
    """
    Safe public representation of a user.
    Never includes password_hash.
    """
    id: str
    name: str
    email: str
    created_at: datetime


class RegisterResponse(BaseModel):
    """Returned after successful registration."""
    message: str = "User registered successfully."
    user: UserResponse
    token: TokenResponse