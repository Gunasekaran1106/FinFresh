import logging
from pymongo.errors import PyMongoError

from app.database import get_database
from app.schemas.dashboard import DashboardSummaryResponse

logger = logging.getLogger(__name__)

TRANSACTIONS_COLLECTION = "transactions"


# ---------------------------------------------------------------------------
# Financial Health Score
# ---------------------------------------------------------------------------

def calculate_financial_health_score(
    total_income: float,
    total_expense: float,
) -> int:
    """
    Compute a financial health score in the range [0, 100].

    Algorithm
    ---------
    Base score  : 50   (neutral starting point)
    Savings bonus: savings_rate * 40
        savings_rate = (income - expenses) / income
        Range: [-∞, 1]. Negative when spending exceeds income.
    Efficiency bonus: max(0, (1 - expense_ratio) * 10)
        expense_ratio = expenses / income
        Rewards low expense ratios with up to 10 extra points.

    Edge cases
    ----------
    - income <= 0  → score = 0  (no income means no basis for scoring)
    - expenses > income → savings_rate is negative, dragging the score below 50
    - Result is clamped to [0, 100] and rounded to the nearest integer.

    Args:
        total_income:  Total income amount (must be >= 0).
        total_expense: Total expense amount (must be >= 0).

    Returns:
        Integer score in [0, 100].
    """
    if total_income <= 0:
        return 0

    savings_rate = (total_income - total_expense) / total_income
    expense_ratio = total_expense / total_income

    score = 50.0
    score += savings_rate * 40
    score += max(0.0, (1.0 - expense_ratio) * 10)

    return int(min(100, max(0, round(score))))


# ---------------------------------------------------------------------------
# Aggregation query
# ---------------------------------------------------------------------------

async def get_dashboard_summary(user_id: str) -> DashboardSummaryResponse:
    """
    Return a financial summary for *user_id* using a single MongoDB
    aggregation pipeline.

    The pipeline groups all transactions for the user in one round-trip,
    computing income totals, expense totals, and counts simultaneously.

    Raises:
        RuntimeError: on unexpected database errors.
    """
    db = get_database()
    col = db[TRANSACTIONS_COLLECTION]

    pipeline = [
        # ── Stage 1: restrict to this user's documents only ──────────────
        {
            "$match": {
                "user_id": user_id,
            }
        },

        # ── Stage 2: group everything in a single pass ───────────────────
        # We use $cond inside $sum to split income and expense totals
        # without two separate queries.
        {
            "$group": {
                "_id": None,                         # collapse to one document
                "total_income": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$type", "income"]},
                            "$amount",
                            0,
                        ]
                    }
                },
                "total_expense": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$type", "expense"]},
                            "$amount",
                            0,
                        ]
                    }
                },
                "income_transaction_count": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$type", "income"]},
                            1,
                            0,
                        ]
                    }
                },
                "expense_transaction_count": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$type", "expense"]},
                            1,
                            0,
                        ]
                    }
                },
                "transaction_count": {"$sum": 1},
            }
        },

        # ── Stage 3: shape the output document ───────────────────────────
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
        raise RuntimeError("Database error while computing dashboard summary.") from exc

    # ── Handle zero-transaction case ─────────────────────────────────────
    # If the user has no transactions the $group stage emits nothing.
    # Return a zeroed-out summary instead of a 404 — an empty dashboard
    # is a valid state for a new user.
    if not results:
        return DashboardSummaryResponse(
            total_income=0.0,
            total_expense=0.0,
            current_balance=0.0,
            financial_health_score=0,
            transaction_count=0,
            income_transaction_count=0,
            expense_transaction_count=0,
        )

    row = results[0]

    total_income = float(row.get("total_income", 0.0))
    total_expense = float(row.get("total_expense", 0.0))
    current_balance = round(total_income - total_expense, 2)

    health_score = calculate_financial_health_score(total_income, total_expense)

    logger.debug(
        "Dashboard for user %s — income=%.2f expense=%.2f balance=%.2f score=%d",
        user_id, total_income, total_expense, current_balance, health_score,
    )

    return DashboardSummaryResponse(
        total_income=total_income,
        total_expense=total_expense,
        current_balance=current_balance,
        financial_health_score=health_score,
        transaction_count=int(row.get("transaction_count", 0)),
        income_transaction_count=int(row.get("income_transaction_count", 0)),
        expense_transaction_count=int(row.get("expense_transaction_count", 0)),
    )