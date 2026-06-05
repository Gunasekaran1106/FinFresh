from typing import List, Literal, Dict
from pydantic import BaseModel, Field, ConfigDict


class DashboardSummaryResponse(BaseModel):
    """
    Financial summary returned by GET /api/v1/summary.
    Matches the public API spec: `income`, `expense`, `savings`, `savingsRate`, `categories`.
    """
    model_config = ConfigDict(populate_by_name=True)

    income: float = Field(
        ...,
        description="Sum of all income transactions for the month.",
        examples=[80000.00],
    )
    expense: float = Field(
        ...,
        description="Sum of all expense transactions for the month.",
        examples=[52000.00],
    )
    savings: float = Field(
        ...,
        description="Savings for the month (income - expense).",
        examples=[28000.00],
    )
    savings_rate: float = Field(
        ...,
        alias="savingsRate",
        ge=0,
        le=100,
        description="Savings rate as a percentage (0-100).",
        examples=[35.0],
    )
    categories: Dict[str, float] = Field(
        default_factory=dict,
        description="Sum of transaction amounts grouped by category.",
        examples=[{"Housing": 20000.00, "Food": 12000.00}],
    )


class FinancialHealthBreakdown(BaseModel):
    """Component scores for financial health calculation."""
    model_config = ConfigDict(populate_by_name=True, alias_generator=None)
    
    emergency_fund: int = Field(
        ...,
        ge=0,
        le=25,
        alias="emergencyFund",
        description="Emergency fund score based on savings coverage months.",
        examples=[20],
    )
    savings_rate: int = Field(
        ...,
        ge=0,
        le=25,
        alias="savingsRate",
        description="Savings rate score based on monthly savings percentage.",
        examples=[25],
    )
    debt_ratio: int = Field(
        ...,
        ge=0,
        le=25,
        alias="debtRatio",
        description="Debt ratio score based on monthly debt-to-income percentage.",
        examples=[25],
    )
    investment_ratio: int = Field(
        ...,
        ge=0,
        le=25,
        alias="investmentRatio",
        description="Investment ratio score based on monthly investment-to-income percentage.",
        examples=[15],
    )


class FinancialHealthResponse(BaseModel):
    """Financial health assessment returned by GET /api/v1/dashboard/financial-health."""
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall financial health score (0-100, sum of 4 components × 25).",
        examples=[85],
    )
    category: Literal["Excellent", "Healthy", "Moderate", "At Risk"] = Field(
        ...,
        description=(
            "Health category: Excellent (80+), Healthy (60-79), Moderate (40-59), At Risk (<40)."
        ),
        examples=["Healthy"],
    )
    breakdown: FinancialHealthBreakdown = Field(
        ...,
        description="Individual component scores.",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations based on component scores.",
        examples=[[
            "Increase your savings rate.",
            "Reduce debt obligations.",
        ]],
    )