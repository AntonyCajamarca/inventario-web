from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, NivelUsuario, EstadoUsuario
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.nombre.asc()).all()


def create_user(db: Session, data: UserCreate) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado.",
        )

    user = User(
        nombre=data.nombre,
        email=data.email,
        password_hash=hash_password(data.password),
        nivel=data.nivel,
        estado=EstadoUsuario.activo,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _count_active_admins(db: Session) -> int:
    return (
        db.query(User)
        .filter(User.nivel == NivelUsuario.admin, User.estado == EstadoUsuario.activo)
        .count()
    )


def update_user(db: Session, user_id: int, data: UserUpdate, current_user: User) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no fue encontrado."
        )

    # Evita que un admin se quite a si mismo el nivel admin o se desactive,
    # si es el ultimo admin activo del sistema.
    perdiendo_admin = data.nivel is not None and data.nivel != NivelUsuario.admin
    desactivando = data.estado is not None and data.estado != EstadoUsuario.activo
    es_el_mismo = user.id == current_user.id

    if user.nivel == NivelUsuario.admin and (perdiendo_admin or desactivando):
        if _count_active_admins(db) <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede quitar el último administrador activo del sistema.",
            )

    if es_el_mismo and (perdiendo_admin or desactivando):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes quitarte tu propio nivel de administrador o desactivar tu cuenta.",
        )

    if data.nombre is not None:
        user.nombre = data.nombre
    if data.nivel is not None:
        user.nivel = data.nivel
    if data.estado is not None:
        user.estado = data.estado
    if data.password:
        user.password_hash = hash_password(data.password)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, current_user: User) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no fue encontrado."
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta.",
        )

    if user.nivel == NivelUsuario.admin and _count_active_admins(db) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el último administrador activo del sistema.",
        )

    db.delete(user)
    db.commit()
