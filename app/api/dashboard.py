from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardOut
from app.services import dashboard_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Panel de control"])


@router.get("", response_model=DashboardOut)
def get_dashboard(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """
    Cualquier usuario autenticado (admin o vendedor) puede ver el panel de control.
    """
    return dashboard_service.get_dashboard(db)
