"""
Centralised HTTP exception handlers.

Each handler maps one custom exception type to an HTTP status code and a
clean JSON body. Registered on the FastAPI app in main.py.
"""
import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    UserNotFoundError,
    TokenExpiredError,
    TokenInvalidError,
    TransactionNotFoundError,
    InvalidObjectIdError,
    DatabaseError,
    AppError,
)

logger = logging.getLogger(__name__)


def _json(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )


# ---------------------------------------------------------------------------
# Per-exception handlers
# ---------------------------------------------------------------------------

async def duplicate_email_handler(request: Request, exc: DuplicateEmailError):
    return _json(status.HTTP_409_CONFLICT, exc.message)


async def invalid_credentials_handler(
    request: Request, exc: InvalidCredentialsError
):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return _json(status.HTTP_404_NOT_FOUND, exc.message)


async def token_expired_handler(request: Request, exc: TokenExpiredError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def token_invalid_handler(request: Request, exc: TokenInvalidError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def transaction_not_found_handler(
    request: Request, exc: TransactionNotFoundError
):
    return _json(status.HTTP_404_NOT_FOUND, exc.message)


async def invalid_object_id_handler(request: Request, exc: InvalidObjectIdError):
    return _json(status.HTTP_400_BAD_REQUEST, exc.message)


async def database_error_handler(request: Request, exc: DatabaseError):
    logger.error("DatabaseError on %s %s: %s", request.method, request.url, exc.message)
    return _json(status.HTTP_500_INTERNAL_SERVER_ERROR, exc.message)


async def app_error_handler(request: Request, exc: AppError):
    """Catch-all for any AppError subclass not handled above."""
    logger.warning("Unhandled AppError: %s", exc.message)
    return _json(status.HTTP_500_INTERNAL_SERVER_ERROR, exc.message)


# ---------------------------------------------------------------------------
# Validation + unhandled
# ---------------------------------------------------------------------------

async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    errors = []
    for error in exc.errors():
        field = " → ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({"field": field or "request", "message": error["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation failed.", "errors": errors},
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )