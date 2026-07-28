from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class FormatoReporte(str, Enum):
    json = "json"
    pdf = "pdf"
    imagen = "imagen"


class VentaResumenOut(BaseModel):
    numero_venta: int
    hora: datetime
    vendedor: str
    productos: str
    total: Decimal


class VentasDiaOut(BaseModel):
    fecha: date
    total_ventas: int
    total_ingresos: Decimal
    ventas: list[VentaResumenOut]


class VentasPorFechaOut(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    total_ventas: int
    total_ingresos: Decimal
    ventas: list[VentaResumenOut]


class VentasMensualesDiaOut(BaseModel):
    fecha: date
    total_ventas: int
    total_ingresos: Decimal


class VentasMensualesOut(BaseModel):
    anio: int
    mes: int
    total_ventas: int
    total_ingresos: Decimal
    dias: list[VentasMensualesDiaOut]


class ProductoStockBajoOut(BaseModel):
    codigo: str
    nombre: str
    categoria: str
    stock: int
    estado_stock: str


class StockBajoOut(BaseModel):
    total_productos: int
    productos: list[ProductoStockBajoOut]


class ProductoMasVendidoOut(BaseModel):
    nombre: str
    total_vendido: int
    cantidad_total: int


class MasVendidosOut(BaseModel):
    productos: list[ProductoMasVendidoOut]
