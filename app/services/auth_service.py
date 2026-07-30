from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User, EstadoUsuario
from app.schemas.user import PasswordChangeIn
from app.utils.security import verify_password, decode_access_token, hash_password

# Esquema simple de Bearer token: en Swagger, boton "Authorize" solo pide
# pegar el access_token (sin usuario/contraseña, ya que el login es JSON).
bearer_scheme = HTTPBearer()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Busca al usuario por email, valida la contraseña y que este activo.
    Nunca revela si el error fue el email o la contraseña (mensaje generico).
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if user.estado != EstadoUsuario.activo:
        return None

    user.ultimo_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependencia para proteger rutas: valida el token y devuelve el usuario."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la sesión, por favor inicia sesión de nuevo.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_error

    email = payload.get("sub")
    if email is None:
        raise credentials_error

    user = db.query(User).filter(User.email == email).first()
    if user is None or user.estado != EstadoUsuario.activo:
        raise credentials_error

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Dependencia para proteger rutas exclusivas de administrador."""
    if user.nivel.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para realizar esta acción.",
        )
    return user


def change_own_password(db: Session, user: User, data: PasswordChangeIn) -> None:
    """El propio usuario cambia su contraseña; requiere la contraseña actual correcta."""
    if not verify_password(data.password_actual, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual no es correcta.",
        )

    user.password_hash = hash_password(data.password_nueva)
    db.commit()
