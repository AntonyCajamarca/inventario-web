from datetime import date, datetime, time

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.sale import Sale, SaleDetail
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleOut, SaleDetailOut, SaleListOut


def _agrupar_items(items) -> dict[int, int]:
    """Combina cantidades si el mismo producto aparece varias veces en la venta."""
    combinado: dict[int, int] = {}
    for item in items:
        combinado[item.producto_id] = combinado.get(item.producto_id, 0) + item.cantidad
    return combinado


def create_sale(db: Session, data: SaleCreate, current_user: User) -> SaleOut:
    items_combinados = _agrupar_items(data.items)

    # 1. Validar todo ANTES de modificar nada (para no dejar la venta a medias)
    productos: dict[int, Product] = {}
    for producto_id, cantidad in items_combinados.items():
        product = db.query(Product).filter(Product.id == producto_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El producto con id {producto_id} no fue encontrado.",
            )
        if product.stock <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"❌ Producto agotado: {product.nombre}.",
            )
        if cantidad > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"❌ No existe suficiente stock de {product.nombre}. "
                    f"Disponible: {product.stock}, solicitado: {cantidad}."
                ),
            )
        productos[producto_id] = product

    # 2. Todo valido: crear la venta, el detalle, y descontar stock
    try:
        total = sum(productos[pid].precio * cant for pid, cant in items_combinados.items())

        sale = Sale(total=total, usuario_id=current_user.id)
        db.add(sale)
        db.flush()  # para obtener sale.id sin cerrar la transaccion

        detalles_out = []
        for producto_id, cantidad in items_combinados.items():
            product = productos[producto_id]
            detail = SaleDetail(
                venta_id=sale.id,
                producto_id=product.id,
                cantidad=cantidad,
                precio_unitario=product.precio,
            )
            db.add(detail)
            product.stock -= cantidad

            detalles_out.append(
                SaleDetailOut(
                    producto_id=product.id,
                    producto=product.nombre,
                    cantidad=cantidad,
                    precio_unitario=product.precio,
                    subtotal=product.precio * cantidad,
                )
            )

        db.commit()
        db.refresh(sale)
    except Exception:
        db.rollback()
        raise

    return SaleOut(
        id=sale.id,
        fecha=sale.fecha,
        total=sale.total,
        vendedor=current_user.nombre,
        detalles=detalles_out,
    )


def get_sale(db: Session, sale_id: int) -> SaleOut:
    sale = (
        db.query(Sale)
        .options(joinedload(Sale.detalles).joinedload(SaleDetail.producto), joinedload(Sale.usuario))
        .filter(Sale.id == sale_id)
        .first()
    )
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="La venta no fue encontrada."
        )

    detalles = [
        SaleDetailOut(
            producto_id=d.producto_id,
            producto=d.producto.nombre,
            cantidad=d.cantidad,
            precio_unitario=d.precio_unitario,
            subtotal=d.precio_unitario * d.cantidad,
        )
        for d in sale.detalles
    ]
    return SaleOut(
        id=sale.id, fecha=sale.fecha, total=sale.total, vendedor=sale.usuario.nombre, detalles=detalles
    )


def list_sales(
    db: Session,
    fecha: date | None = None,
    producto: str | None = None,
    numero_venta: int | None = None,
) -> list[SaleListOut]:
    query = db.query(Sale).options(
        joinedload(Sale.detalles).joinedload(SaleDetail.producto), joinedload(Sale.usuario)
    )

    if numero_venta is not None:
        query = query.filter(Sale.id == numero_venta)

    if fecha is not None:
        inicio = datetime.combine(fecha, time.min)
        fin = datetime.combine(fecha, time.max)
        query = query.filter(Sale.fecha.between(inicio, fin))

    if producto:
        texto = f"%{producto.strip()}%"
        query = query.join(SaleDetail).join(Product).filter(Product.nombre.ilike(texto))

    ventas = query.order_by(Sale.fecha.desc()).distinct().all()

    resultado = []
    for sale in ventas:
        nombres = ", ".join(d.producto.nombre for d in sale.detalles)
        resultado.append(
            SaleListOut(
                id=sale.id,
                fecha=sale.fecha,
                total=sale.total,
                vendedor=sale.usuario.nombre,
                productos=nombres,
                cantidad_items=len(sale.detalles),
            )
        )
    return resultado
