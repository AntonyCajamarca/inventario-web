from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import NivelUsuario, EstadoUsuario


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class UserOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    nivel: NivelUsuario
    estado: EstadoUsuario
    foto: str | None = None
    fecha_creacion: datetime
    ultimo_login: datetime | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserCreate(BaseModel):
    """Usado por el modulo de Accesos (solo admin puede crear usuarios)."""
    nombre: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    nivel: NivelUsuario = NivelUsuario.vendedor


class UserUpdate(BaseModel):
    """
    Usado por el modulo de Accesos para editar un usuario existente.
    Todos los campos son opcionales: solo se actualiza lo que se envie.
    La contraseña es opcional -> si viene vacia, no se cambia.
    """
    nombre: str | None = Field(default=None, min_length=2, max_length=120)
    nivel: NivelUsuario | None = None
    estado: EstadoUsuario | None = None
    password: str | None = Field(default=None, min_length=8, max_length=100)


class PasswordChangeIn(BaseModel):
    """Usado por el propio usuario para cambiar su contraseña (requiere la actual)."""
    password_actual: str = Field(min_length=1)
    password_nueva: str = Field(min_length=8, max_length=100)
