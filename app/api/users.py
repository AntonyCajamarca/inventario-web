from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.services import user_service
from app.services.auth_service import require_admin

router = APIRouter(prefix="/api/users", tags=["Accesos (usuarios)"])


@router.get("", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return user_service.list_users(db)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    return user_service.create_user(db, data)


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return user_service.update_user(db, user_id, data, current_user=admin)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user_service.delete_user(db, user_id, current_user=admin)
    return {"success": True, "message": "Usuario eliminado correctamente"}
