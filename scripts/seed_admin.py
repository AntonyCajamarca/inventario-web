"""
Script de arranque del proyecto.

Uso (desde la raiz del proyecto, con el entorno virtual activado):
    python -m scripts.seed_admin

Que hace:
1. Espera a que la base de datos este lista para aceptar conexiones
   (reintenta varias veces con pausas, util en Railway/Azure donde el
   servicio de base de datos puede tardar unos segundos en arrancar).
2. Crea las tablas en la base de datos si no existen.
3. Crea la cuenta admin (ADMIN_EMAIL) definida en el .env, solo si no existe ya.

Este script se puede correr las veces que quieras: si el admin ya existe,
no hace nada (evita duplicados).
"""

import time

from sqlalchemy.exc import OperationalError

from app.config import settings
from app.database.base import Base
from app.database.session import engine, SessionLocal
import app.models  # noqa: F401  (registra todos los modelos en Base.metadata)
from app.models.user import User, NivelUsuario, EstadoUsuario
from app.utils.security import hash_password

MAX_INTENTOS = 10
ESPERA_SEGUNDOS = 3


def esperar_base_de_datos():
    """Reintenta la conexion varias veces antes de rendirse."""
    for intento in range(1, MAX_INTENTOS + 1):
        try:
            with engine.connect():
                print("Conexión a la base de datos exitosa.")
                return
        except OperationalError as e:
            print(
                f"Intento {intento}/{MAX_INTENTOS}: la base de datos aún no responde "
                f"({e.__class__.__name__}). Reintentando en {ESPERA_SEGUNDOS}s..."
            )
            time.sleep(ESPERA_SEGUNDOS)

    raise RuntimeError(
        f"No se pudo conectar a la base de datos después de {MAX_INTENTOS} intentos."
    )


def run():
    esperar_base_de_datos()

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
