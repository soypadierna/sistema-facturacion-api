from fastapi import APIRouter, Depends
from app.core.deps import require_permission
from app.features.dashboard import service
from app.features.dashboard.schemas import DashboardOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("", response_model=DashboardOut, response_model_by_alias=True)
def get_dashboard(user=Depends(require_permission("dashboard"))):
    return service.get_dashboard(user.rol_id)