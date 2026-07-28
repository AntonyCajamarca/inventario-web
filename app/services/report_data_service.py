import calendar
from datetime import date, datetime, time

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models.category import Category
from app.models.product import Product
from app.models.sale import Sale, SaleDetail
from app.schemas.report import (
    VentaResumenOut,
    VentasDiaOut,
    VentasPorFechaOut,
    VentasMensualesOut,
    VentasMensualesDiaOut,
    StockBajoOut,
    ProductoStockBajoOut,
    MasVendidosOut,
    ProductoMasVendidoOut,
)


def _ventas_en_rango(db: Session, inicio: datetime, fin: datetime) -> list[Sale]:
    return (
        db.query(Sale)
        .options(joinedload(Sale.detalles).joinedload(SaleDetail.producto), joinedload(Sale.usuario))
        .filter(Sale.fecha.between(inicio, fin))
        .order_by(Sale.fecha.asc())
        .all()
    )


def _to_resumen(sale: Sale) -> VentaResumenOut:
    nombres = ", ".join(d.producto.nombre for d in sale.detalles)
    return VentaResumenOut(
        numero_venta=sale.id,
        hora=sale.fecha,
        vendedor=sale.usuario.nombre,
        productos=nombres,
        total=sale.total,
    )


def get_ventas_dia(db: Session, fecha: date) -> VentasDiaOut:
    inicio = datetime.combine(fecha, time.min)
    fin = datetime.combine(fecha, time.max)
    ventas = _ventas_en_rango(db, inicio, fin)

    return VentasDiaOut(
        fecha=fecha,
        total_ventas=len(ventas),
        total_ingresos=sum((v.total for v in ventas), start=0),
        ventas=[_to_resumen(v) for v in ventas],
    )


def get_ventas_por_fecha(db: Session, fecha_inicio: date, fecha_fin: date) -> VentasPorFechaOut:
    if fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de inicio no puede ser mayor que la fecha final.",
        )

    inicio = datetime.combine(fecha_inicio, time.min)
    fin = datetime.combine(fecha_fin, time.max)
    ventas = _ventas_en_rango(db, inicio, fin)

    return VentasPorFechaOut(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        total_ventas=len(ventas),
        total_ingresos=sum((v.total for v in ventas), start=0),
        ventas=[_to_resumen(v) for v in ventas],
    )


def get_ventas_mensuales(db: Session, anio: int, mes: int) -> VentasMensualesOut:
    if mes < 1 or mes > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El mes debe estar entre 1 y 12."
        )

    ultimo_dia = calendar.monthrange(anio, mes)[1]
    inicio = datetime(anio, mes, 1, 0, 0, 0)
    fin = datetime(anio, mes, ultimo_dia, 23, 59, 59)
    ventas = _ventas_en_rango(db, inicio, fin)

    por_dia: dict[date, list[Sale]] = {}
    for v in ventas:
        dia = v.fecha.date()
        por_dia.setdefault(dia, []).append(v)

    dias = [
        VentasMensualesDiaOut(
            fecha=dia,
            total_ventas=len(lista),
            total_ingresos=sum((v.total for v in lista), start=0),
        )
        for dia, lista in sorted(por_dia.items())
    ]

    return VentasMensualesOut(
        anio=anio,
        mes=mes,
        total_ventas=len(ventas),
        total_ingresos=sum((v.total for v in ventas), start=0),
        dias=dias,
    )


def get_stock_bajo(db: Session) -> StockBajoOut:
    productos = (
        db.query(Product)
        .options(joinedload(Product.categoria))
        .filter(Product.stock <= settings.STOCK_BAJO_UMBRAL)
        .order_by(Product.stock.asc())
        .all()
    )

    salida = [
        ProductoStockBajoOut(
            codigo=p.codigo,
            nombre=p.nombre,
            categoria=p.categoria.nombre,
            stock=p.stock,
            estado_stock="agotado" if p.stock <= 0 else "bajo",
        )
        for p in productos
    ]
    return StockBajoOut(total_productos=len(salida), productos=salida)


def get_mas_vendidos(db: Session, limite: int) -> MasVendidosOut:
    rows = (
        db.query(
            Product.nombre.label("nombre"),
            func.count(SaleDetail.id).label("total_vendido"),
            func.coalesce(func.sum(SaleDetail.cantidad), 0).label("cantidad_total"),
        )
        .join(SaleDetail, SaleDetail.producto_id == Product.id)
        .group_by(Product.id, Product.nombre)
        .order_by(func.sum(SaleDetail.cantidad).desc())
        .limit(limite)
        .all()
    )
    productos = [ProductoMasVendidoOut(**row._mapping) for row in rows]
    return MasVendidosOut(productos=productos)
