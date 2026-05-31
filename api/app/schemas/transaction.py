from datetime import datetime, timezone
from typing import Optional, Literal, List
from pydantic import BaseModel, Field, field_validator


class TransactionCreateRequest(BaseModel):
    """Payload for POST /api/v1/transactions"""
    type: Literal["income", "expense"] = Field(..., examples=["income"])
    category: str = Field(..., min_length=1, max_length=100, examples=["Salary"])
    amount: float = Field(..., gt=0, examples=[5000.00])
    description: str = Field(..., min_length=1, max_length=500, examples=["Monthly salary"])
    date: datetime = Field(
        ...,
        examples=["2025-06-01T00:00:00Z"],
        description="ISO-8601 datetime for the transaction. UTC recommended.",
    )

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category must not be blank.")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Description must not be blank.")
        return v.strip()

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(v, 2)


class TransactionResponse(BaseModel):
    """Public representation of a single transaction."""
    id: str
    user_id: str
    type: Literal["income", "expense"]
    category: str
    amount: float
    description: str
    date: datetime
    created_at: datetime


class TransactionListResponse(BaseModel):
    """Paginated list of transactions."""
    total: int
    transactions: List[TransactionResponse]


class TransactionDeleteResponse(BaseModel):
    message: str = "Transaction deleted successfully."
    transaction_id: str