import logging
from typing import Optional

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from app.database import get_database
from app.models.user import UserDocument
from app.schemas.auth import RegisterRequest, UserResponse, TokenResponse, RegisterResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings

logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _get_users_collection():
    db = get_database()
    return db[USERS_COLLECTION]


async def ensure_user_indexes() -> None:
    """
    Create a unique index on email.
    Called once at startup — safe to call repeatedly (idempotent).
    """
    col = await _get_users_collection()
    await col.create_index(
        [("email", ASCENDING)],
        unique=True,
        name="email_unique",
    )
    logger.info("User indexes ensured.")


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

async def get_user_by_email(email: str) -> Optional[UserDocument]:
    """Return a UserDocument for the given email, or None if not found."""
    col = await _get_users_collection()
    raw = await col.find_one({"email": email.lower().strip()})
    return UserDocument.from_mongo(raw) if raw else None


async def get_user_by_id(user_id: str) -> Optional[UserDocument]:
    """Return a UserDocument for the given string id, or None if not found."""
    from bson import ObjectId
    col = await _get_users_collection()
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    raw = await col.find_one({"_id": oid})
    return UserDocument.from_mongo(raw) if raw else None


def _build_user_response(user: UserDocument) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
    )


def _build_token_response(user_id: str) -> TokenResponse:
    token = create_access_token(subject=user_id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


async def register_user(payload: RegisterRequest) -> RegisterResponse:
    """
    Create a new user.

    Raises:
        ValueError: if the email is already registered.
    """
    col = await _get_users_collection()

    doc = UserDocument(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hash_password(payload.password),
    )

    try:
        result = await col.insert_one(doc.to_mongo())
    except DuplicateKeyError:
        raise ValueError("An account with this email already exists.")

    inserted_id = str(result.inserted_id)
    doc.id = inserted_id

    logger.info("New user registered: %s (id=%s)", doc.email, inserted_id)

    return RegisterResponse(
        user=_build_user_response(doc),
        token=_build_token_response(inserted_id),
    )


async def login_user(email: str, password: str) -> dict:
    """
    Authenticate a user by email + password.

    Returns:
        Dict with keys 'user' (UserResponse) and 'token' (TokenResponse).

    Raises:
        ValueError: on invalid credentials (intentionally vague to prevent
                    user enumeration attacks).
    """
    INVALID_CREDENTIALS_MSG = "Invalid email or password."

    user = await get_user_by_email(email)
    if user is None:
        raise ValueError(INVALID_CREDENTIALS_MSG)

    if not verify_password(password, user.password_hash):
        logger.debug("Failed login attempt for email: %s", email)
        raise ValueError(INVALID_CREDENTIALS_MSG)

    logger.info("User logged in: %s (id=%s)", user.email, user.id)

    return {
        "user": _build_user_response(user),
        "token": _build_token_response(user.id),
    }