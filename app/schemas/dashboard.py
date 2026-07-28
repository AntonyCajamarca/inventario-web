from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class DashboardCounts(BaseModel):
    usuarios: int
    categorias: int
    productos: int
    ventas: int


class TopProductOut(BaseModel):
    producto_id: int
    nombre: str
    total_vendido: int  # numero de veces que aparecio en una venta
    cantidad_total: int  # suma de unidades vendidas


class RecentSaleOut(BaseModel):
    id: int
    fecha: datetime
    total: Decimal
    vendedor: str


class RecentProductOut(BaseModel):
    id: int
    nombre: str
    precio: Decimal
    categoria: str
    fecha_creacion: datetime


class DashboardOut(BaseModel):
    counts: DashboardCounts
    productos_mas_vendidos: list[TopProductOut]
    ultimas_ventas: list[RecentSaleOut]
    productos_recientes: list[RecentProductOut]
