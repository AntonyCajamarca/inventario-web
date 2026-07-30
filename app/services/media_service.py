import os
import secrets

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.models.media import Media
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductOut
from app.schemas.user import UserOut
from app.services.product_service import _to_out

EXTENSIONES_PERMITIDAS = {"gif", "jpg", "jpeg", "png"}
TIPOS_MIME_PERMITIDOS = {"image/gif", "image/jpeg", "image/png"}


def _carpeta_productos() -> str:
    carpeta = os.path.join(settings.UPLOADS_DIR, "products")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def _carpeta_usuarios() -> str:
    carpeta = os.path.join(settings.UPLOADS_DIR, "users")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


def _validar_archivo(file: UploadFile, contenido: bytes) -> str:
    if not file.filename or "." not in file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Archivo inválido."
        )

    extension = file.filename.rsplit(".", 1)[1].lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de archivo incorrecto. Solo se permiten: gif, jpg, jpeg, png.",
        )

    if file.content_type not in TIPOS_MIME_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no es una imagen válida.",
        )

    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(contenido) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La imagen supera el tamaño máximo permitido ({settings.MAX_UPLOAD_MB} MB).",
        )

    return extension


def _eliminar_archivo_fisico(carpeta: str, file_name: str) -> None:
    ruta = os.path.join(carpeta, file_name)
    if os.path.exists(ruta):
        os.remove(ruta)


def upload_product_media(db: Session, producto_id: int, file: UploadFile) -> ProductOut:
    product = db.query(Product).filter(Product.id == producto_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El producto no fue encontrado."
        )

    contenido = file.file.read()
    extension = _validar_archivo(file, contenido)

    # Numero de serie aleatorio para que el nombre del archivo nunca choque
    serie = secrets.token_hex(6)
    nombre_final = f"{serie}_{product.codigo}.{extension}"

    ruta_destino = os.path.join(_carpeta_productos(), nombre_final)
    with open(ruta_destino, "wb") as f:
        f.write(contenido)

    media_anterior = product.media

    media = Media(file_name=nombre_final, file_type=file.content_type)
    db.add(media)
    db.flush()

    product.media_id = media.id
    db.commit()
    db.refresh(product)

    # Limpiar la imagen anterior (archivo + registro), ya que el producto
    # ahora apunta a la nueva
    if media_anterior:
        _eliminar_archivo_fisico(_carpeta_productos(), media_anterior.file_name)
        db.delete(media_anterior)
        db.commit()

    return _to_out(product)


def delete_product_media(db: Session, producto_id: int) -> None:
    product = db.query(Product).filter(Product.id == producto_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El producto no fue encontrado."
        )

    if not product.media:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este producto no tiene una imagen asignada.",
        )

    media = product.media
    product.media_id = None
    db.commit()

    _eliminar_archivo_fisico(_carpeta_productos(), media.file_name)
    db.delete(media)
    db.commit()


def upload_user_photo(db: Session, user: User, file: UploadFile) -> UserOut:
    contenido = file.file.read()
    extension = _validar_archivo(file, contenido)

    serie = secrets.token_hex(6)
    nombre_final = f"{serie}_user{user.id}.{extension}"

    ruta_destino = os.path.join(_carpeta_usuarios(), nombre_final)
    with open(ruta_destino, "wb") as f:
        f.write(contenido)

    media_anterior = user.media

    media = Media(file_name=nombre_final, file_type=file.content_type)
    db.add(media)
    db.flush()

    user.media_id = media.id
    db.commit()
    db.refresh(user)

    if media_anterior:
        _eliminar_archivo_fisico(_carpeta_usuarios(), media_anterior.file_name)
        db.delete(media_anterior)
        db.commit()

    return UserOut.model_validate(user)


def delete_user_photo(db: Session, user: User) -> None:
    if not user.media:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tienes una foto de perfil asignada.",
        )

    media = user.media
    user.media_id = None
    db.commit()

    _eliminar_archivo_fisico(_carpeta_usuarios(), media.file_name)
    db.delete(media)
    db.commit()
