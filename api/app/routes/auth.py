import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import register_user, login_user
from app.middleware.auth import CurrentUser

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /api/v1/auth/register
# ---------------------------------------------------------------------------
@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User created successfully."},
        409: {"description": "Email already registered."},
        422: {"description": "Validation error."},
    },
)
async def register(payload: RegisterRequest):
    """
    Create a new user account and return a JWT so the client is
    immediately authenticated without a separate login step.
    """
    try:
        result = await register_user(payload)
        return result
    except ValueError as exc:
        # auth_service raises ValueError for duplicate email
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# ---------------------------------------------------------------------------
# POST /api/v1/auth/login
# ---------------------------------------------------------------------------
@router.post(
    "/login",
    response_model=RegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    responses={
        200: {"description": "Login successful."},
        401: {"description": "Invalid credentials."},
        422: {"description": "Validation error."},
    },
)
async def login(payload: LoginRequest):
    """
    Authenticate with email + password and receive a JWT access token.
    """
    try:
        result = await login_user(payload.email, payload.password)
        return RegisterResponse(
            message="Login successful.",
            user=result["user"],
            token=result["token"],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# GET /api/v1/auth/me   — protected
# ---------------------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user",
    responses={
        200: {"description": "Current user profile."},
        401: {"description": "Missing or invalid token."},
    },
)
async def get_me(current_user: CurrentUser):
    """
    Return the profile of the currently authenticated user.
    Requires a valid Bearer token in the Authorization header.
    """
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
    )