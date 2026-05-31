import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_access_token
from app.services.auth_service import get_user_by_id
from app.models.user import UserDocument

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HTTPBearer extracts the token from the Authorization: Bearer <token> header.
# auto_error=False lets us return a custom 401 instead of FastAPI's default.
# ---------------------------------------------------------------------------
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ],
) -> UserDocument:
    """
    FastAPI dependency that validates a JWT and returns the authenticated user.

    Inject with:
        current_user: Annotated[UserDocument, Depends(get_current_user)]

    Raises:
        HTTP 401 — missing token, expired token, invalid token, user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        logger.debug("Token decode failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user = await get_user_by_id(user_id)
    if user is None:
        # Token was valid but the account no longer exists
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# Convenient type alias — use this in every protected route
CurrentUser = Annotated[UserDocument, Depends(get_current_user)]