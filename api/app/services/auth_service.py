import logging
from typing import Optional

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.database import get_database
from app.models.user import UserDocument
from app.schemas.auth import RegisterRequest, UserResponse, TokenResponse, RegisterResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.core.exceptions import (
    DuplicateEmailError,
    InvalidCredentialsError,
    UserNotFoundError,
    DatabaseError,
)

logger = logging.getLogger(__name__)

USERS_COLLECTION = "users"


async def _get_users_collection():
    return get_database()[USERS_COLLECTION]


async def ensure_user_indexes() -> None:
    col = await _get_users_collection()
    await col.create_index(
        [("email", ASCENDING)],
        unique=True,
        name="email_unique",
    )
    logger.info("User indexes ensured.")


async def get_user_by_email(email: str) -> Optional[UserDocument]:
    try:
        col = await _get_users_collection()
        raw = await col.find_one({"email": email.lower().strip()})
        return UserDocument.from_mongo(raw) if raw else None
    except PyMongoError as exc:
        logger.exception("DB error fetching user by email.")
        raise DatabaseError() from exc


async def get_user_by_id(user_id: str) -> Optional[UserDocument]:
    from bson import ObjectId
    try:
        col = await _get_users_collection()
        oid = ObjectId(user_id)
        raw = await col.find_one({"_id": oid})
        return UserDocument.from_mongo(raw) if raw else None
    except Exception as exc:
        # ObjectId() raises if user_id is malformed — treat as not found
        logger.debug("get_user_by_id failed for id=%s: %s", user_id, exc)
        return None


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
    col = await _get_users_collection()
    doc = UserDocument(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hash_password(payload.password),
    )
    try:
        result = await col.insert_one(doc.to_mongo())
    except DuplicateKeyError:
        raise DuplicateEmailError()
    except PyMongoError as exc:
        logger.exception("DB error during registration.")
        raise DatabaseError() from exc

    inserted_id = str(result.inserted_id)
    doc.id = inserted_id
    logger.info("New user registered: %s (id=%s)", doc.email, inserted_id)

    return RegisterResponse(
        user=_build_user_response(doc),
        token=_build_token_response(inserted_id),
    )


async def login_user(email: str, password: str) -> dict:
    user = await get_user_by_email(email)
    if user is None or not verify_password(password, user.password_hash):
        logger.debug("Failed login attempt for email: %s", email)
        raise InvalidCredentialsError()

    logger.info("User logged in: %s (id=%s)", user.email, user.id)
    return {
        "user": _build_user_response(user),
        "token": _build_token_response(user.id),
    }