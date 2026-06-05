import logging
from fastapi import APIRouter, status
from app.middleware.auth import CurrentUser
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.finance_service import get_dashboard_summary

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get monthly financial summary",
)
async def summary(current_user: CurrentUser):
    return await get_dashboard_summary(user_id=current_user.id)
