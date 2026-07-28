from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.report import FormatoReporte
from app.services import report_data_service as data_service
from app.services import report_render_service as render_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/reports", tags=["Reportes"])


def _responder(formato: FormatoReporte, datos_json, *, title, meta_lines, headers, rows, total_line, filename_base):
    if formato == FormatoReporte.json:
        return datos_json

    if formato == FormatoReporte.pdf:
        contenido = render_service.render_pdf(title, meta_lines, headers, rows, total_line)
        media_type = "application/pdf"
        filename = f"{filename_base}.pdf"
    else:
        contenido = render_service.render_image(title, meta_lines, headers, rows, total_line)
        media_type = "image/png"
        filename = f"{filename_base}.png"

    return Response(
        content=contenido,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/ventas-dia")
def reporte_ventas_dia(
    fecha: date = Query(default_factory=date.today),
    formato: FormatoReporte = Query(default=FormatoReporte.json),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    datos = data_service.get_ventas_dia(db, fecha)

    headers = ["N° venta", "Hora", "Vendedor", "Productos", "Total"]
    rows = [
        [v.numero_venta, v.hora.strftime("%H:%M:%S"), v.vendedor, v.productos, f"${v.total:.2f}"]
        for v in datos.ventas
    ]
    return _responder(
        formato,
        datos,
        title=f"Reporte de ventas del día {fecha.isoformat()}",
        meta_lines=[f"Total de ventas: {datos.total_ventas}"],
        headers=headers,
        rows=rows,
        total_line=f"Total ingresos: ${datos.total_ingresos:.2f}",
        filename_base=f"ventas_dia_{fecha.isoformat()}",
    )


@router.get("/ventas-por-fecha")
def reporte_ventas_por_fecha(
    fecha_inicio: date,
    fecha_fin: date,
    formato: FormatoReporte = Query(default=FormatoReporte.json),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    datos = data_service.get_ventas_por_fecha(db, fecha_inicio, fecha_fin)

    headers = ["N° venta", "Fecha", "Vendedor", "Productos", "Total"]
    rows = [
        [
            v.numero_venta,
            v.hora.strftime("%d/%m/%Y %H:%M"),
            v.vendedor,
            v.productos,
            f"${v.total:.2f}",
        ]
        for v in datos.ventas
    ]
    return _responder(
        formato,
        datos,
        title=f"Reporte de ventas del {fecha_inicio.isoformat()} al {fecha_fin.isoformat()}",
        meta_lines=[f"Total de ventas: {datos.total_ventas}"],
        headers=headers,
        rows=rows,
        total_line=f"Total ingresos: ${datos.total_ingresos:.2f}",
        filename_base=f"ventas_{fecha_inicio.isoformat()}_a_{fecha_fin.isoformat()}",
    )


@router.get("/ventas-mensuales")
def reporte_ventas_mensuales(
    anio: int,
    mes: int,
    formato: FormatoReporte = Query(default=FormatoReporte.json),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    datos = data_service.get_ventas_mensuales(db, anio, mes)

    headers = ["Fecha", "N° de ventas", "Ingresos"]
    rows = [
        [d.fecha.isoformat(), d.total_ventas, f"${d.total_ingresos:.2f}"] for d in datos.dias
    ]
    return _responder(
        formato,
        datos,
        title=f"Reporte de ventas mensuales {mes:02d}/{anio}",
        meta_lines=[f"Total de ventas del mes: {datos.total_ventas}"],
        headers=headers,
        rows=rows,
        total_line=f"Total ingresos del mes: ${datos.total_ingresos:.2f}",
        filename_base=f"ventas_mensuales_{anio}_{mes:02d}",
    )


@router.get("/stock-bajo")
def reporte_stock_bajo(
    formato: FormatoReporte = Query(default=FormatoReporte.json),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    datos = data_service.get_stock_bajo(db)

    headers = ["Código", "Producto", "Categoría", "Stock", "Estado"]
    rows = [
        [p.codigo, p.nombre, p.categoria, p.stock, "❌ Agotado" if p.estado_stock == "agotado" else "⚠ Bajo"]
        for p in datos.productos
    ]
    return _responder(
        formato,
        datos,
        title="Reporte de productos con poco stock",
        meta_lines=[f"Total de productos con stock bajo o agotado: {datos.total_productos}"],
        headers=headers,
        rows=rows,
        total_line=None,
        filename_base="productos_stock_bajo",
    )


@router.get("/mas-vendidos")
def reporte_mas_vendidos(
    limite: int = Query(default=10, ge=1, le=100),
    formato: FormatoReporte = Query(default=FormatoReporte.json),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    datos = data_service.get_mas_vendidos(db, limite)

    headers = ["Producto", "N° de ventas", "Cantidad total vendida"]
    rows = [[p.nombre, p.total_vendido, p.cantidad_total] for p in datos.productos]
    return _responder(
        formato,
        datos,
        title=f"Reporte de los {limite} productos más vendidos",
        meta_lines=[],
        headers=headers,
        rows=rows,
        total_line=None,
        filename_base="productos_mas_vendidos",
    )
