from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleOut, SaleListOut
from app.services import sale_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/sales", tags=["Ventas"])


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(
    data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return sale_service.create_sale(db, data, current_user)


@router.get("", response_model=list[SaleListOut])
def get_sales(
    fecha: date | None = Query(default=None, description="Filtrar por fecha exacta (YYYY-MM-DD)"),
    producto: str | None = Query(default=None, description="Filtrar por nombre de producto"),
    numero_venta: int | None = Query(default=None, description="Filtrar por número de venta"),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return sale_service.list_sales(db, fecha=fecha, producto=producto, numero_venta=numero_venta)


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(
    sale_id: int, db: Session = Depends(get_db), _user: User = Depends(get_current_user)
):
    return sale_service.get_sale(db, sale_id)
