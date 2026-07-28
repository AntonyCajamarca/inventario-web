import enum
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class NivelUsuario(str, enum.Enum):
    admin = "admin"
    vendedor = "vendedor"


class EstadoUsuario(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nivel: Mapped[NivelUsuario] = mapped_column(
        Enum(NivelUsuario), default=NivelUsuario.vendedor, nullable=False
    )
    estado: Mapped[EstadoUsuario] = mapped_column(
        Enum(EstadoUsuario), default=EstadoUsuario.activo, nullable=False
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ultimo_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
