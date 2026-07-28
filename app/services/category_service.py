from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut


def _to_out(db: Session, category: Category) -> CategoryOut:
    total = db.query(func.count(Product.id)).filter(
        Product.categoria_id == category.id
    ).scalar() or 0
    return CategoryOut(
        id=category.id,
        nombre=category.nombre,
        descripcion=category.descripcion,
        fecha_creacion=category.fecha_creacion,
        total_productos=total,
    )


def list_categories(db: Session) -> list[CategoryOut]:
    categories = db.query(Category).order_by(Category.nombre.asc()).all()
    return [_to_out(db, c) for c in categories]


def _find_by_name(db: Session, nombre: str, exclude_id: int | None = None) -> Category | None:
    query = db.query(Category).filter(func.lower(Category.nombre) == nombre.lower().strip())
    if exclude_id is not None:
        query = query.filter(Category.id != exclude_id)
    return query.first()


def create_category(db: Session, data: CategoryCreate) -> CategoryOut:
    if _find_by_name(db, data.nombre):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una categoría con ese nombre.",
        )

    category = Category(nombre=data.nombre.strip(), descripcion=data.descripcion)
    db.add(category)
    db.commit()
    db.refresh(category)
    return _to_out(db, category)


def update_category(db: Session, category_id: int, data: CategoryUpdate) -> CategoryOut:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La categoría no fue encontrada.",
        )

    if data.nombre is not None:
        if _find_by_name(db, data.nombre, exclude_id=category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre.",
            )
        category.nombre = data.nombre.strip()

    if data.descripcion is not None:
        category.descripcion = data.descripcion

    db.commit()
    db.refresh(category)
    return _to_out(db, category)


def delete_category(db: Session, category_id: int) -> None:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La categoría no fue encontrada.",
        )

    total_productos = db.query(func.count(Product.id)).filter(
        Product.categoria_id == category_id
    ).scalar() or 0

    if total_productos > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se puede eliminar esta categoría porque tiene "
                f"{total_productos} producto(s) asociado(s)."
            ),
        )

    db.delete(category)
    db.commit()
