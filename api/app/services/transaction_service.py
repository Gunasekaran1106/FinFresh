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

logger = logging.getLogger(__name__)

TRANSACTIONS_COLLECTION = "transactions"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_collection():
    """Return the transactions collection from the active database."""
    return get_database()[TRANSACTIONS_COLLECTION]


def _doc_to_response(doc: TransactionDocument) -> TransactionResponse:
    """Convert an internal TransactionDocument to a public TransactionResponse."""
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


def _build_object_id(raw_id: str) -> ObjectId:
    """
    Parse a string into a BSON ObjectId.

    Raises:
        ValueError: if the string is not a valid ObjectId.
    """
    try:
        return ObjectId(raw_id)
    except Exception:
        raise ValueError(f"'{raw_id}' is not a valid ID.")


# ---------------------------------------------------------------------------
# Index setup
# ---------------------------------------------------------------------------

async def ensure_transaction_indexes() -> None:
    """
    Create indexes for common query patterns.
    Called once at startup — idempotent.

    Indexes created:
      1. (user_id, date DESC)  — list transactions for a user sorted by date
      2. (user_id, type)       — filter by income / expense per user
      3. (user_id, created_at) — secondary sort by insertion order
    """
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


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

async def create_transaction(
    user_id: str,
    payload: TransactionCreateRequest,
) -> TransactionResponse:
    """
    Insert a new transaction for *user_id*.

    Raises:
        RuntimeError: on unexpected database errors.
    """
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
        raise RuntimeError("Database error while saving transaction.") from exc

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
    """
    Return a paginated list of transactions for *user_id*.

    Args:
        user_id:          Authenticated user's string id.
        transaction_type: Optional filter — 'income' or 'expense'.
        skip:             Number of documents to skip (for pagination).
        limit:            Maximum documents to return (capped at 100).

    Returns:
        TransactionListResponse with total count and page of transactions.
    """
    col = _get_collection()

    # Hard cap — prevents accidentally fetching thousands of documents
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
        raise RuntimeError("Database error while fetching transactions.") from exc

    transactions = [
        _doc_to_response(TransactionDocument.from_mongo(raw))
        for raw in raw_docs
    ]

    return TransactionListResponse(total=total, transactions=transactions)


async def delete_transaction(
    user_id: str,
    transaction_id: str,
) -> TransactionDeleteResponse:
    """
    Delete a single transaction.

    Ownership is enforced — a user can only delete their own transactions.

    Raises:
        ValueError:  transaction_id is not a valid ObjectId format.
        LookupError: transaction not found or belongs to another user.
        RuntimeError: unexpected database error.
    """
    col = _get_collection()

    try:
        oid = _build_object_id(transaction_id)
    except ValueError:
        raise ValueError(f"Invalid transaction ID: '{transaction_id}'.")

    query = {
        "_id": oid,
        "user_id": user_id,   # ownership check — never delete another user's data
    }

    try:
        result = await col.delete_one(query)
    except PyMongoError as exc:
        logger.exception(
            "Failed to delete transaction %s for user %s", transaction_id, user_id
        )
        raise RuntimeError("Database error while deleting transaction.") from exc

    if result.deleted_count == 0:
        raise LookupError(
            f"Transaction '{transaction_id}' not found or does not belong to you."
        )

    logger.info("Transaction deleted: id=%s user=%s", transaction_id, user_id)
    return TransactionDeleteResponse(transaction_id=transaction_id)