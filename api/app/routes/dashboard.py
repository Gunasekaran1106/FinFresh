import logging

from fastapi import APIRouter, HTTPException, status

from app.middleware.auth import CurrentUser
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.finance_service import get_dashboard_summary

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /api/v1/dashboard/summary
# ---------------------------------------------------------------------------
@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get financial dashboard summary",
    responses={
        200: {"description": "Financial summary computed successfully."},
        401: {"description": "Missing or invalid token."},
        500: {"description": "Database aggregation error."},
    },
)
async def dashboard_summary(current_user: CurrentUser):
    """
    Return a financial summary for the authenticated user.

    Includes:
    - **total_income** — sum of all income transactions
    - **total_expense** — sum of all expense transactions
    - **current_balance** — income minus expenses
    - **financial_health_score** — 0–100 score based on savings rate and
      expense ratio. Returns **0** when no income is recorded.
    - **transaction_count** — total transactions
    - **income_transaction_count** — number of income entries
    - **expense_transaction_count** — number of expense entries

    All values are computed in a single MongoDB aggregation pipeline.
    New users with no transactions receive a zeroed summary (not an error).
    """
    try:
        return await get_dashboard_summary(user_id=current_user.id)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )