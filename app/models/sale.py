from datetime import datetime

from sqlalchemy import Integer, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Sale(Base):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    usuario_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    usuario: Mapped["User"] = relationship()

    detalles: Mapped[list["SaleDetail"]] = relationship(
        back_populates="venta", cascade="all, delete-orphan"
    )


class SaleDetail(Base):
    __tablename__ = "detalle_ventas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    venta_id: Mapped[int] = mapped_column(ForeignKey("ventas.id"), nullable=False)
    venta: Mapped["Sale"] = relationship(back_populates="detalles")

    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), nullable=False)
    producto: Mapped["Product"] = relationship()

    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
