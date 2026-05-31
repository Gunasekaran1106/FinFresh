import logging
from typing import Optional, Literal
from fastapi import APIRouter, status, Query
from app.middleware.auth import CurrentUser
from app.schemas.transaction import (
    TransactionCreateRequest, TransactionResponse,
    TransactionListResponse, TransactionDeleteResponse,
)
from app.services.transaction_service import (
    create_transaction, get_transactions, delete_transaction,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new transaction",
)
async def add_transaction(
    payload: TransactionCreateRequest,
    current_user: CurrentUser,
):
    # DatabaseError → 500 via global handler
    return await create_transaction(user_id=current_user.id, payload=payload)


@router.get(
    "/",
    response_model=TransactionListResponse,
    status_code=status.HTTP_200_OK,
    summary="List transactions with optional filtering and pagination",
)
async def list_transactions(
    current_user: CurrentUser,
    type: Optional[Literal["income", "expense"]] = Query(
        default=None,
        description="Filter by transaction type.",
    ),
    skip: int = Query(default=0, ge=0, description="Pagination offset."),
    limit: int = Query(default=20, ge=1, le=100, description="Page size (max 100)."),
):
    # DatabaseError → 500 via global handler
    return await get_transactions(
        user_id=current_user.id,
        transaction_type=type,
        skip=skip,
        limit=limit,
    )


@router.delete(
    "/{transaction_id}",
    response_model=TransactionDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a transaction by ID",
)
async def remove_transaction(
    transaction_id: str,
    current_user: CurrentUser,
):
    # InvalidObjectIdError   → 400 via global handler
    # TransactionNotFoundError → 404 via global handler
    # DatabaseError          → 500 via global handler
    return await delete_transaction(
        user_id=current_user.id,
        transaction_id=transaction_id,
    )