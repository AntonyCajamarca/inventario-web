from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.config import settings
from app.models.category import Category
from app.models.product import Product
from app.models.sale import SaleDetail
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductPriceUpdate,
    ProductStockUpdate,
    ProductOut,
)


def _estado_stock(stock: int) -> str:
    if stock <= 0:
        return "agotado"
    if stock <= settings.STOCK_BAJO_UMBRAL:
        return "bajo"
    return "disponible"


def _to_out(product: Product) -> ProductOut:
    imagen_url = f"/uploads/products/{product.media.file_name}" if product.media else None
    return ProductOut(
        id=product.id,
        codigo=product.codigo,
        nombre=product.nombre,
        descripcion=product.descripcion,
        categoria_id=product.categoria_id,
        categoria=product.categoria.nombre,
        precio=product.precio,
        stock=product.stock,
        estado_stock=_estado_stock(product.stock),
        imagen=imagen_url,
        fecha_creacion=product.fecha_creacion,
        fecha_actualizacion=product.fecha_actualizacion,
    )


def _get_category_or_404(db: Session, categoria_id: int) -> Category:
    category = db.query(Category).filter(Category.id == categoria_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La categoría seleccionada no existe.",
        )
    return category


def _find_by_codigo(db: Session, codigo: str, exclude_id: int | None = None) -> Product | None:
    query = db.query(Product).filter(func.lower(Product.codigo) == codigo.lower().strip())
    if exclude_id is not None:
        query = query.filter(Product.id != exclude_id)
    return query.first()


def list_products(db: Session, buscar: str | None = None) -> list[ProductOut]:
    query = db.query(Product)
    if buscar:
        texto = f"%{buscar.strip()}%"
        query = query.filter(or_(Product.nombre.ilike(texto), Product.codigo.ilike(texto)))
    products = query.order_by(Product.nombre.asc()).all()
    return [_to_out(p) for p in products]


def get_product(db: Session, product_id: int) -> ProductOut:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El producto no fue encontrado."
        )
    return _to_out(product)


def create_product(db: Session, data: ProductCreate) -> ProductOut:
    if _find_by_codigo(db, data.codigo):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El código ya existe."
        )
    _get_category_or_404(db, data.categoria_id)

    product = Product(
        codigo=data.codigo.strip(),
        nombre=data.nombre.strip(),
        descripcion=data.descripcion,
        categoria_id=data.categoria_id,
        precio=data.precio,
        stock=data.stock,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return _to_out(product)


def _get_product_or_404(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El producto no fue encontrado."
        )
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> ProductOut:
    product = _get_product_or_404(db, product_id)

    if data.codigo is not None:
        if _find_by_codigo(db, data.codigo, exclude_id=product_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="El código ya existe."
            )
        product.codigo = data.codigo.strip()

    if data.categoria_id is not None:
        _get_category_or_404(db, data.categoria_id)
        product.categoria_id = data.categoria_id

    if data.nombre is not None:
        product.nombre = data.nombre.strip()
    if data.descripcion is not None:
        product.descripcion = data.descripcion
    if data.precio is not None:
        product.precio = data.precio
    if data.stock is not None:
        product.stock = data.stock

    db.commit()
    db.refresh(product)
    return _to_out(product)


def update_price(db: Session, product_id: int, data: ProductPriceUpdate) -> ProductOut:
    product = _get_product_or_404(db, product_id)
    product.precio = data.precio
    db.commit()
    db.refresh(product)
    return _to_out(product)


def update_stock(db: Session, product_id: int, data: ProductStockUpdate) -> ProductOut:
    product = _get_product_or_404(db, product_id)
    product.stock = data.stock
    db.commit()
    db.refresh(product)
    return _to_out(product)


def delete_product(db: Session, product_id: int) -> None:
    product = _get_product_or_404(db, product_id)

    tiene_ventas = db.query(func.count(SaleDetail.id)).filter(
        SaleDetail.producto_id == product_id
    ).scalar() or 0

    if tiene_ventas > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede eliminar este producto porque tiene "
                f"{tiene_ventas} venta(s) registrada(s) en el historial."
            ),
        )

    db.delete(product)
    db.commit()
