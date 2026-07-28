from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class SaleItemCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0)


class SaleCreate(BaseModel):
    items: list[SaleItemCreate]

    @field_validator("items")
    @classmethod
    def no_vacio(cls, items):
        if not items:
            raise ValueError("La venta debe tener al menos un producto.")
        return items


class SaleDetailOut(BaseModel):
    producto_id: int
    producto: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal


class SaleOut(BaseModel):
    id: int  # se usa tambien como numero de venta
    fecha: datetime
    total: Decimal
    vendedor: str
    detalles: list[SaleDetailOut]


class SaleListOut(BaseModel):
    """Version resumida para el listado del historial (sin el detalle completo)."""
    id: int
    fecha: datetime
    total: Decimal
    vendedor: str
    productos: str  # nombres de productos separados por coma, para la vista de tabla
    cantidad_items: int
