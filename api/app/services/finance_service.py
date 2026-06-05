import logging
from datetime import datetime, timezone, timedelta
from pymongo.errors import PyMongoError

from app.database import get_database
from app.schemas.dashboard import DashboardSummaryResponse, FinancialHealthResponse, FinancialHealthBreakdown
from app.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

TRANSACTIONS_COLLECTION = "transactions"


def calculate_financial_health_score(
    total_income: float,
    total_expense: float,
) -> int:
    if total_income <= 0:
        return 0

    savings_rate = (total_income - total_expense) / total_income
    expense_ratio = total_expense / total_income

    score = 50.0
    score += savings_rate * 40
    score += max(0.0, (1.0 - expense_ratio) * 10)

    return int(min(100, max(0, round(score))))


async def get_dashboard_summary(user_id: str) -> DashboardSummaryResponse:
    db = get_database()
    col = db[TRANSACTIONS_COLLECTION]

    # Main aggregation for summary metrics
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": None,
                "total_income": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]
                    }
                },
                "total_expense": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]
                    }
                },
                "income_transaction_count": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "income"]}, 1, 0]
                    }
                },
                "expense_transaction_count": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "expense"]}, 1, 0]
                    }
                },
                "transaction_count": {"$sum": 1},
            }
        },
        {
            "$project": {
                "_id": 0,
                "total_income": {"$round": ["$total_income", 2]},
                "total_expense": {"$round": ["$total_expense", 2]},
                "income_transaction_count": 1,
                "expense_transaction_count": 1,
                "transaction_count": 1,
            }
        },
    ]

    try:
        results = await col.aggregate(pipeline).to_list(length=1)
    except PyMongoError as exc:
        logger.exception("Aggregation failed for user %s", user_id)
        raise DatabaseError() from exc

    if not results:
        return DashboardSummaryResponse(
            income=0.0,
            expense=0.0,
            savings=0.0,
            savingsRate=0.0,
            categories={},
        )

    row = results[0]
    total_income = float(row.get("total_income", 0.0))
    total_expense = float(row.get("total_expense", 0.0))

    # Calculate savings and savings rate (monthly)
    savings = round(total_income - total_expense, 2)
    if total_income > 0:
        savings_rate = round((savings / total_income) * 100, 1)
    else:
        savings_rate = 0.0

    # Get category aggregation
    category_pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"},
            }
        },
    ]

    try:
        category_results = await col.aggregate(category_pipeline).to_list(length=None)
    except PyMongoError as exc:
        logger.exception("Category aggregation failed for user %s", user_id)
        category_results = []

    # Convert category results to dict
    categories = {
        item["_id"]: round(item["total"], 2)
        for item in category_results
        if item["_id"]
    }

    return DashboardSummaryResponse(
        income=round(total_income, 2),
        expense=round(total_expense, 2),
        savings=round(savings, 2),
        savingsRate=savings_rate,
        categories=categories,
    )


async def _get_monthly_metrics(user_id: str) -> dict:
    """Get income, expense, investment, and debt totals for current month."""
    db = get_database()
    col = db[TRANSACTIONS_COLLECTION]

    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "date": {"$gte": month_start},
            }
        },
        {
            "$group": {
                "_id": None,
                "income": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]
                    }
                },
                "expense": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]
                    }
                },
                "investment": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "investment"]}, "$amount", 0]
                    }
                },
                "debt": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "debt"]}, "$amount", 0]
                    }
                },
            }
        },
    ]

    try:
        results = await col.aggregate(pipeline).to_list(length=1)
    except PyMongoError as exc:
        logger.exception("Monthly metrics aggregation failed for user %s", user_id)
        return {
            "income": 0.0,
            "expense": 0.0,
            "investment": 0.0,
            "debt": 0.0,
        }

    if not results:
        return {
            "income": 0.0,
            "expense": 0.0,
            "investment": 0.0,
            "debt": 0.0,
        }

    row = results[0]
    return {
        "income": float(row.get("income", 0.0)),
        "expense": float(row.get("expense", 0.0)),
        "investment": float(row.get("investment", 0.0)),
        "debt": float(row.get("debt", 0.0)),
    }


async def _get_last_three_months_expenses(user_id: str) -> float:
    """Get average monthly expense for last 3 months."""
    db = get_database()
    col = db[TRANSACTIONS_COLLECTION]

    now = datetime.now(timezone.utc)
    three_months_ago = now - timedelta(days=90)

    pipeline = [
        {
            "$match": {
                "user_id": user_id,
                "type": "expense",
                "date": {"$gte": three_months_ago},
            }
        },
        {
            "$group": {
                "_id": None,
                "total_expense": {"$sum": "$amount"},
            }
        },
    ]

    try:
        results = await col.aggregate(pipeline).to_list(length=1)
    except PyMongoError as exc:
        logger.exception(
            "Last 3 months expense aggregation failed for user %s", user_id
        )
        return 0.0

    if not results:
        return 0.0

    row = results[0]
    total_expense = float(row.get("total_expense", 0.0))
    return round(total_expense / 3, 2)


async def _get_all_time_metrics(user_id: str) -> dict:
    """Get all-time income and expense totals (for emergency fund calculation)."""
    db = get_database()
    col = db[TRANSACTIONS_COLLECTION]

    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": None,
                "total_income": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "income"]}, "$amount", 0]
                    }
                },
                "total_expense": {
                    "$sum": {
                        "$cond": [{"$eq": ["$type", "expense"]}, "$amount", 0]
                    }
                },
            }
        },
    ]

    try:
        results = await col.aggregate(pipeline).to_list(length=1)
    except PyMongoError as exc:
        logger.exception("All-time metrics aggregation failed for user %s", user_id)
        return {"total_income": 0.0, "total_expense": 0.0}

    if not results:
        return {"total_income": 0.0, "total_expense": 0.0}

    row = results[0]
    return {
        "total_income": float(row.get("total_income", 0.0)),
        "total_expense": float(row.get("total_expense", 0.0)),
    }


def _calculate_emergency_fund_score(
    total_savings: float,
    avg_monthly_expense: float,
) -> int:
    """
    Calculate emergency fund score (0-25 points).
    Emergency fund = how many months of expenses savings can cover.
    """
    if avg_monthly_expense == 0:
        return 25

    coverage = total_savings / avg_monthly_expense

    if coverage < 1:
        return 5
    elif coverage < 3:
        return 10
    elif coverage < 6:
        return 20
    else:
        return 25


def _calculate_savings_rate_score(
    monthly_income: float,
    monthly_expense: float,
) -> int:
    """Calculate savings rate score (0-25 points) for current month."""
    if monthly_income == 0:
        return 0

    savings_rate = ((monthly_income - monthly_expense) / monthly_income) * 100

    if savings_rate < 10:
        return 5
    elif savings_rate < 20:
        return 10
    elif savings_rate < 40:
        return 20
    else:
        return 25


def _calculate_debt_ratio_score(
    monthly_income: float,
    monthly_debt: float,
) -> int:
    """Calculate debt ratio score (0-25 points) for current month."""
    if monthly_income == 0:
        return 0

    debt_ratio = (monthly_debt / monthly_income) * 100

    if debt_ratio > 50:
        return 5
    elif debt_ratio > 30:
        return 10
    elif debt_ratio > 10:
        return 20
    else:
        return 25


def _calculate_investment_ratio_score(
    monthly_income: float,
    monthly_investment: float,
) -> int:
    """Calculate investment ratio score (0-25 points) for current month."""
    if monthly_income == 0:
        return 0

    investment_ratio = (monthly_investment / monthly_income) * 100

    if investment_ratio < 5:
        return 5
    elif investment_ratio < 15:
        return 10
    elif investment_ratio < 30:
        return 20
    else:
        return 25


async def calculate_financial_health(user_id: str) -> FinancialHealthResponse:
    """
    Calculate comprehensive financial health score with 4 components:
    - Emergency Fund: based on months of expenses saved
    - Savings Rate: based on current month savings percentage
    - Debt Ratio: based on current month debt-to-income ratio
    - Investment Ratio: based on current month investment-to-income ratio
    """
    # Get current month metrics
    monthly_metrics = await _get_monthly_metrics(user_id)
    monthly_income = monthly_metrics["income"]
    monthly_expense = monthly_metrics["expense"]
    monthly_investment = monthly_metrics["investment"]
    monthly_debt = monthly_metrics["debt"]

    # Get all-time metrics for emergency fund
    all_time_metrics = await _get_all_time_metrics(user_id)
    total_income_all_time = all_time_metrics["total_income"]
    total_expense_all_time = all_time_metrics["total_expense"]
    total_savings = total_income_all_time - total_expense_all_time

    # Get 3-month average expense
    avg_monthly_expense = await _get_last_three_months_expenses(user_id)

    # Calculate component scores
    emergency_points = _calculate_emergency_fund_score(total_savings, avg_monthly_expense)
    savings_points = _calculate_savings_rate_score(monthly_income, monthly_expense)
    debt_points = _calculate_debt_ratio_score(monthly_income, monthly_debt)
    investment_points = _calculate_investment_ratio_score(
        monthly_income, monthly_investment
    )

    # Total score
    total_score = emergency_points + savings_points + debt_points + investment_points

    # Determine category
    if total_score >= 80:
        category = "Excellent"
    elif total_score >= 60:
        category = "Healthy"
    elif total_score >= 40:
        category = "Moderate"
    else:
        category = "At Risk"

    # Generate suggestions
    suggestions = []
    if savings_points < 20:
        suggestions.append("Increase your savings rate.")
    if debt_points < 20:
        suggestions.append("Reduce debt obligations.")
    if investment_points < 20:
        suggestions.append("Increase investment contributions.")
    if emergency_points < 20:
        suggestions.append("Build an emergency fund.")

    breakdown = FinancialHealthBreakdown(
        emergency_fund=emergency_points,
        savings_rate=savings_points,
        debt_ratio=debt_points,
        investment_ratio=investment_points,
    )

    return FinancialHealthResponse(
        score=total_score,
        category=category,
        breakdown=breakdown,
        suggestions=suggestions,
    )