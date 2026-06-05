import datetime as dt
from datetime import datetime, timezone
from typing import Optional, Literal, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class TransactionCreateRequest(BaseModel):
    """Payload for POST /api/v1/transactions"""
    type: Literal["income", "expense", "investment", "debt"] = Field(..., examples=["income"])
    category: str = Field(..., min_length=1, max_length=100, examples=["Salary"])
    amount: float = Field(..., gt=0, examples=[5000.00])
    description: Optional[str] = Field(default=None, max_length=500, examples=["Monthly salary"])
    date: dt.date = Field(
        ...,
        examples=["2025-06-01"],
        description="Date of the transaction (YYYY-MM-DD format).",
    )

    @field_validator("category")
    @classmethod
    def category_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError("Category must not be blank.")
        return v.strip()

    @field_validator("description", mode="before")
    @classmethod
    def description_must_not_be_blank(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            raise ValueError("Description must not be blank.")
        return v.strip() if isinstance(v, str) else v

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(v, 2)


class TransactionResponse(BaseModel):
    """Public representation of a single transaction."""
    model_config = ConfigDict(populate_by_name=True)

    id: str
    type: Literal["income", "expense", "investment", "debt"]
    category: str
    amount: float
    description: Optional[str] = None
    date: dt.date
    created_at: datetime = Field(alias="createdAt")


class PaginationInfo(BaseModel):
    """Pagination metadata for transaction list."""
    page: int = Field(
        ...,
        ge=1,
        description="Page number (1-based).",
        examples=[1],
    )
    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Page size.",
        examples=[20],
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of transactions for this user.",
        examples=[100],
    )


class TransactionListResponse(BaseModel):
    """Paginated list of transactions."""
    data: List[TransactionResponse] = Field(
        ...,
        description="Array of transaction objects.",
    )
    pagination: PaginationInfo = Field(
        ...,
        description="Pagination metadata.",
    )


class TransactionDeleteResponse(BaseModel):
    message: str = "Transaction deleted successfully."
    transaction_id: str