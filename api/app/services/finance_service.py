import logging
from pymongo.errors import PyMongoError

from app.database import get_database
from app.schemas.dashboard import DashboardSummaryResponse
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

    return DashboardSummaryResponse(
        total_income=total_income,
        total_expense=total_expense,
        current_balance=round(total_income - total_expense, 2),
        financial_health_score=calculate_financial_health_score(
            total_income, total_expense
        ),
        transaction_count=int(row.get("transaction_count", 0)),
        income_transaction_count=int(row.get("income_transaction_count", 0)),
        expense_transaction_count=int(row.get("expense_transaction_count", 0)),
    )