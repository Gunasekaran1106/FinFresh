import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",          # automatically re-hash old schemes
    bcrypt__rounds=12,          # work factor — increase for stronger hashing
)


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of *plain_password*."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Return True if *plain_password* matches *hashed_password*.
    Uses a constant-time comparison internally to resist timing attacks.
    """
    return _pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

def create_access_token(
    subject: str,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Create a signed JWT.

    Args:
        subject:      The value to store in the 'sub' claim (user id as string).
        extra_claims: Optional additional claims merged into the payload.

    Returns:
        Encoded JWT string.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload: dict = {
        "sub": subject,
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT.

    Returns:
        The decoded payload dict.

    Raises:
        ValueError: with a human-readable message on any JWT problem.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "access":
            raise ValueError("Invalid token type.")
        return payload

    except ExpiredSignatureError:
        logger.debug("JWT has expired.")
        raise ValueError("Token has expired. Please log in again.")
    except JWTError as exc:
        logger.debug("JWT decode error: %s", exc)
        raise ValueError("Invalid token. Authentication failed.")