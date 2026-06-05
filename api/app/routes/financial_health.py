import logging
from fastapi import APIRouter, status
from app.middleware.auth import CurrentUser
from app.schemas.dashboard import FinancialHealthResponse
from app.services.finance_service import calculate_financial_health

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/financial-health",
    response_model=FinancialHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get comprehensive financial health assessment",
)
async def financial_health(current_user: CurrentUser):
    # DatabaseError → 500 via global handler
    return await calculate_financial_health(user_id=current_user.id)
