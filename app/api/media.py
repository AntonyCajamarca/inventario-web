from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.product import ProductOut
from app.services import media_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/products", tags=["Media"])


@router.post("/{producto_id}/media", response_model=ProductOut)
def upload_media(
    producto_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Sube (o reemplaza) la imagen de un producto."""
    return media_service.upload_product_media(db, producto_id, file)


@router.delete("/{producto_id}/media")
def delete_media(
    producto_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    media_service.delete_product_media(db, producto_id)
    return {"success": True, "message": "Imagen eliminada correctamente"}
