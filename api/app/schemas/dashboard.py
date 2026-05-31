from pydantic import BaseModel, Field


class DashboardSummaryResponse(BaseModel):
    """
    Financial summary returned by GET /api/v1/dashboard/summary.
    All monetary values are rounded to 2 decimal places.
    """
    total_income: float = Field(
        ...,
        description="Sum of all income transactions.",
        examples=[5000.00],
    )
    total_expense: float = Field(
        ...,
        description="Sum of all expense transactions.",
        examples=[1500.00],
    )
    current_balance: float = Field(
        ...,
        description="total_income minus total_expense.",
        examples=[3500.00],
    )
    financial_health_score: int = Field(
        ...,
        ge=0,
        le=100,
        description=(
            "Score from 0–100 reflecting savings rate and expense ratio. "
            "0 = no income recorded. 100 = perfect savings."
        ),
        examples=[78],
    )
    transaction_count: int = Field(
        ...,
        description="Total number of transactions for this user.",
        examples=[12],
    )
    income_transaction_count: int = Field(
        ...,
        description="Number of income transactions.",
        examples=[4],
    )
    expense_transaction_count: int = Field(
        ...,
        description="Number of expense transactions.",
        examples=[8],
    )