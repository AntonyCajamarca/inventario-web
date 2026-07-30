from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.sale import Sale, SaleDetail
from app.schemas.dashboard import (
    DashboardCounts,
    TopProductOut,
    RecentSaleOut,
    RecentProductOut,
    DashboardOut,
)
from app.services import report_data_service

LIMITE_LISTAS = 5


def get_counts(db: Session) -> DashboardCounts:
    return DashboardCounts(
        usuarios=db.query(func.count(User.id)).scalar() or 0,
        categorias=db.query(func.count(Category.id)).scalar() or 0,
        productos=db.query(func.count(Product.id)).scalar() or 0,
        ventas=db.query(func.count(Sale.id)).scalar() or 0,
    )


def get_productos_mas_vendidos(db: Session, limit: int = LIMITE_LISTAS) -> list[TopProductOut]:
    rows = (
        db.query(
            Product.id.label("producto_id"),
            Product.nombre.label("nombre"),
            func.count(SaleDetail.id).label("total_vendido"),
            func.coalesce(func.sum(SaleDetail.cantidad), 0).label("cantidad_total"),
        )
        .join(SaleDetail, SaleDetail.producto_id == Product.id)
        .group_by(Product.id, Product.nombre)
        .order_by(func.sum(SaleDetail.cantidad).desc())
        .limit(limit)
        .all()
    )
    return [TopProductOut(**row._mapping) for row in rows]


def get_ultimas_ventas(db: Session, limit: int = LIMITE_LISTAS) -> list[RecentSaleOut]:
    rows = (
        db.query(
            Sale.id.label("id"),
            Sale.fecha.label("fecha"),
            Sale.total.label("total"),
            User.nombre.label("vendedor"),
        )
        .join(User, User.id == Sale.usuario_id)
        .order_by(Sale.fecha.desc())
        .limit(limit)
        .all()
    )
    return [RecentSaleOut(**row._mapping) for row in rows]


def get_productos_recientes(db: Session, limit: int = LIMITE_LISTAS) -> list[RecentProductOut]:
    rows = (
        db.query(
            Product.id.label("id"),
            Product.nombre.label("nombre"),
            Product.precio.label("precio"),
            Category.nombre.label("categoria"),
            Product.fecha_creacion.label("fecha_creacion"),
        )
        .join(Category, Category.id == Product.categoria_id)
        .order_by(Product.fecha_creacion.desc())
        .limit(limit)
        .all()
    )
    return [RecentProductOut(**row._mapping) for row in rows]


def get_dashboard(db: Session) -> DashboardOut:
    return DashboardOut(
        counts=get_counts(db),
        productos_mas_vendidos=get_productos_mas_vendidos(db),
        ultimas_ventas=get_ultimas_ventas(db),
        productos_recientes=get_productos_recientes(db),
        productos_por_reponer=report_data_service.get_stock_bajo(db).productos,
    )
