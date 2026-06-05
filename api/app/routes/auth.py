import logging
from fastapi import APIRouter, status
from app.schemas.auth import (
    RegisterRequest, LoginRequest,
    RegisterResponse, LoginResponse, UserResponse,
)
from app.services.auth_service import register_user, login_user
from app.middleware.auth import CurrentUser
from app.core.exceptions import DuplicateEmailError, InvalidCredentialsError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        400: {"description": "Email already exists or invalid input"},
    },
)
async def register(payload: RegisterRequest):
    # DuplicateEmailError is caught by the global handler → 400
    return await register_user(payload)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    responses={
        400: {"description": "Validation error or invalid input"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(payload: LoginRequest):
    # InvalidCredentialsError is caught by the global handler → 401
    result = await login_user(payload.email, payload.password)
    return LoginResponse(
        message="Login successful.",
        user=result["user"],
        token=result["token"],
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user",
)
async def get_me(current_user: CurrentUser):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        created_at=current_user.created_at,
    )