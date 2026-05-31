import logging
from typing import Optional, Literal

from fastapi import APIRouter, HTTPException, status, Query

from app.middleware.auth import CurrentUser
from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionResponse,
    TransactionListResponse,
    TransactionDeleteResponse,
)
from app.services.transaction_service import (
    create_transaction,
    get_transactions,
    delete_transaction,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /api/v1/transactions
# ---------------------------------------------------------------------------
@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new transaction (income or expense)",
    responses={
        201: {"description": "Transaction created."},
        401: {"description": "Missing or invalid token."},
        422: {"description": "Validation error."},
        500: {"description": "Database error."},
    },
)
async def add_transaction(
    payload: TransactionCreateRequest,
    current_user: CurrentUser,
):
    """
    Add a new income or expense transaction for the authenticated user.

    - **type**: `"income"` or `"expense"`
    - **amount**: must be greater than 0
    - **date**: ISO-8601 datetime string (e.g. `2025-06-01T00:00:00Z`)
    """
    try:
        return await create_transaction(
            user_id=current_user.id,
            payload=payload,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


# ---------------------------------------------------------------------------
# GET /api/v1/transactions
# ---------------------------------------------------------------------------
@router.get(
    "/",
    response_model=TransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List transactions with optional filtering and pagination",
    responses={
        200: {"description": "Paginated transaction list."},
        401: {"description": "Missing or invalid token."},
        422: {"description": "Validation error (bad query params)."},
        500: {"description": "Database error."},
    },
)
async def list_transactions(
    current_user: CurrentUser,
    type: Optional[Literal["income", "expense"]] = Query(
        default=None,
        description="Filter by transaction type. Omit for all transactions.",
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip (pagination offset).",
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of records to return (1–100).",
    ),
):
    """
    Return transactions for the authenticated user, sorted by date descending.

    **Filtering:**
    - `?type=income` — only income transactions
    - `?type=expense` — only expense transactions
    - *(omit)* — all transactions

    **Pagination:**
    - `?skip=0&limit=20` — first page
    - `?skip=20&limit=20` — second page
    """
    try:
        return await get_transactions(
            user_id=current_user.id,
            transaction_type=type,
            skip=skip,
            limit=limit,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


# ---------------------------------------------------------------------------
# DELETE /api/v1/transactions/{transaction_id}
# ---------------------------------------------------------------------------
@router.delete(
    "/{transaction_id}",
    response_model=TransactionDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a transaction by ID",
    responses={
        200: {"description": "Transaction deleted."},
        400: {"description": "Invalid transaction ID format."},
        401: {"description": "Missing or invalid token."},
        404: {"description": "Transaction not found."},
        500: {"description": "Database error."},
    },
)
async def remove_transaction(
    transaction_id: str,
    current_user: CurrentUser,
):
    """
    Delete a specific transaction.
    Users can only delete their **own** transactions.
    """
    try:
        return await delete_transaction(
            user_id=current_user.id,
            transaction_id=transaction_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )