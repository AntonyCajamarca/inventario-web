from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.product import (
    ProductOut,
    ProductCreate,
    ProductUpdate,
    ProductPriceUpdate,
    ProductStockUpdate,
)
from app.services import product_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/products", tags=["Productos"])


@router.get("", response_model=list[ProductOut])
def get_products(
    buscar: str | None = Query(default=None, description="Buscar por nombre o código"),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return product_service.list_products(db, buscar=buscar)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(
    product_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
):
    return product_service.get_product(db, product_id)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
):
    return product_service.create_product(db, data)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return product_service.update_product(db, product_id, data)


@router.patch("/{product_id}/price", response_model=ProductOut)
def update_price(
    product_id: int,
    data: ProductPriceUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return product_service.update_price(db, product_id, data)


@router.patch("/{product_id}/stock", response_model=ProductOut)
def update_stock(
    product_id: int,
    data: ProductStockUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return product_service.update_stock(db, product_id, data)


@router.delete("/{product_id}")
def delete_product(
    product_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
):
    product_service.delete_product(db, product_id)
    return {"success": True, "message": "Producto eliminado correctamente"}
