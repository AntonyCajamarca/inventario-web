from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    nombre: str = Field(min_length=1, max_length=150)
    descripcion: str | None = Field(default=None, max_length=500)
    categoria_id: int
    precio: Decimal = Field(gt=0)
    stock: int = Field(ge=0)


class ProductUpdate(BaseModel):
    codigo: str | None = Field(default=None, min_length=1, max_length=50)
    nombre: str | None = Field(default=None, min_length=1, max_length=150)
    descripcion: str | None = Field(default=None, max_length=500)
    categoria_id: int | None = None
    precio: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)


class ProductPriceUpdate(BaseModel):
    precio: Decimal = Field(gt=0)


class ProductStockUpdate(BaseModel):
    stock: int = Field(ge=0)


class ProductOut(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: str | None = None
    categoria_id: int
    categoria: str
    precio: Decimal
    stock: int
    estado_stock: str  # "agotado" | "bajo" | "disponible"
    imagen: str | None = None  # URL relativa, ej: /uploads/products/archivo.jpg
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True
