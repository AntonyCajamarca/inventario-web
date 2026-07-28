from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)


class CategoryUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, max_length=255)


class CategoryOut(BaseModel):
    id: int
    nombre: str
    descripcion: str | None = None
    fecha_creacion: datetime
    total_productos: int = 0

    class Config:
        from_attributes = True
