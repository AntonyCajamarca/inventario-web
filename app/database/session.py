from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# echo=False en produccion; puedes poner True temporalmente para depurar SQL
engine = create_engine(settings.DATABASE_URL, echo=False, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependencia de FastAPI: entrega una sesion de base de datos
    y la cierra automaticamente al terminar la peticion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
