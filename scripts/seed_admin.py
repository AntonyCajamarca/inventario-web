"""
Script de arranque del proyecto.

Uso (desde la raiz del proyecto, con el entorno virtual activado):
    python -m scripts.seed_admin

Que hace:
1. Crea las tablas en la base de datos si no existen.
2. Crea la cuenta admin (ADMIN_EMAIL) definida en el .env, solo si no existe ya.

Este script se puede correr las veces que quieras: si el admin ya existe,
no hace nada (evita duplicados).
"""

from app.config import settings
from app.database.base import Base
from app.database.session import engine, SessionLocal
import app.models  # noqa: F401  (registra todos los modelos en Base.metadata)
from app.models.user import User, NivelUsuario, EstadoUsuario
from app.utils.security import hash_password


def run():
    print("Creando tablas (si no existen)...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if existing:
            print(f"El usuario admin '{settings.ADMIN_EMAIL}' ya existe. No se creó nada.")
            return

        admin = User(
            nombre=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            nivel=NivelUsuario.admin,
            estado=EstadoUsuario.activo,
        )
        db.add(admin)
        db.commit()
        print(f"Usuario admin creado correctamente: {settings.ADMIN_EMAIL}")
        print("Recuerda cambiar la contraseña despues del primer inicio de sesión.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
