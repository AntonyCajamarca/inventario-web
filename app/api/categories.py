from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.category import CategoryOut, CategoryCreate, CategoryUpdate
from app.services import category_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/categories", tags=["Categorías"])


@router.get("", response_model=list[CategoryOut])
def get_categories(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return category_service.list_categories(db)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return category_service.create_category(db, data)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return category_service.update_category(db, category_id, data)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    category_service.delete_category(db, category_id)
    return {"success": True, "message": "Categoría eliminada correctamente"}
