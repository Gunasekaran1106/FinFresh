import logging
from datetime import datetime, timezone
from typing import Optional, Literal

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from app.database import get_database
from app.models.transaction import TransactionDocument
from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionResponse,
    TransactionListResponse,
    TransactionDeleteResponse,
)
from app.core.exceptions import (
    InvalidObjectIdError,
    TransactionNotFoundError,
    DatabaseError,
)

logger = logging.getLogger(__name__)

TRANSACTIONS_COLLECTION = "transactions"


def _get_collection():
    return get_database()[TRANSACTIONS_COLLECTION]


def _doc_to_response(doc: TransactionDocument) -> TransactionResponse:
    return TransactionResponse(
        id=doc.id,
        user_id=doc.user_id,
        type=doc.type,
        category=doc.category,
        amount=doc.amount,
        description=doc.description,
        date=doc.date,
        created_at=doc.created_at,
    )


def _parse_object_id(raw_id: str) -> ObjectId:
    try:
        return ObjectId(raw_id)
    except Exception:
        raise InvalidObjectIdError(f"'{raw_id}' is not a valid transaction ID.")


async def ensure_transaction_indexes() -> None:
    col = _get_collection()
    await col.create_index(
        [("user_id", ASCENDING), ("date", DESCENDING)],
        name="user_date_desc",
    )
    await col.create_index(
        [("user_id", ASCENDING), ("type", ASCENDING)],
        name="user_type",
    )
    await col.create_index(
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        name="user_created_at_desc",
    )
    logger.info("Transaction indexes ensured.")


async def create_transaction(
    user_id: str,
    payload: TransactionCreateRequest,
) -> TransactionResponse:
    col = _get_collection()
    doc = TransactionDocument(
        user_id=user_id,
        type=payload.type,
        category=payload.category.strip(),
        amount=round(payload.amount, 2),
        description=payload.description.strip(),
        date=payload.date,
        created_at=datetime.now(timezone.utc),
    )
    try:
        result = await col.insert_one(doc.to_mongo())
    except PyMongoError as exc:
        logger.exception("Failed to insert transaction for user %s", user_id)
        raise DatabaseError() from exc

    doc.id = str(result.inserted_id)
    logger.info(
        "Transaction created: id=%s user=%s type=%s amount=%.2f",
        doc.id, user_id, doc.type, doc.amount,
    )
    return _doc_to_response(doc)


async def get_transactions(
    user_id: str,
    transaction_type: Optional[Literal["income", "expense"]] = None,
    skip: int = 0,
    limit: int = 50,
) -> TransactionListResponse:
    col = _get_collection()
    limit = min(limit, 100)

    query: dict = {"user_id": user_id}
    if transaction_type is not None:
        query["type"] = transaction_type

    try:
        total = await col.count_documents(query)
        cursor = (
            col.find(query)
            .sort([("date", DESCENDING), ("created_at", DESCENDING)])
            .skip(skip)
            .limit(limit)
        )
        raw_docs = await cursor.to_list(length=limit)
    except PyMongoError as exc:
        logger.exception("Failed to fetch transactions for user %s", user_id)
        raise DatabaseError() from exc

    transactions = [
        _doc_to_response(TransactionDocument.from_mongo(raw))
        for raw in raw_docs
    ]
    return TransactionListResponse(total=total, transactions=transactions)


async def delete_transaction(
    user_id: str,
    transaction_id: str,
) -> TransactionDeleteResponse:
    col = _get_collection()
    oid = _parse_object_id(transaction_id)   # raises InvalidObjectIdError if bad

    query = {"_id": oid, "user_id": user_id}
    try:
        result = await col.delete_one(query)
    except PyMongoError as exc:
        logger.exception(
            "Failed to delete transaction %s for user %s", transaction_id, user_id
        )
        raise DatabaseError() from exc

    if result.deleted_count == 0:
        raise TransactionNotFoundError(
            f"Transaction '{transaction_id}' not found or does not belong to you."
        )

    logger.info("Transaction deleted: id=%s user=%s", transaction_id, user_id)
    return TransactionDeleteResponse(transaction_id=transaction_id)