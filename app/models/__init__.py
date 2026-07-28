"""
Este archivo importa todos los modelos para que SQLAlchemy los registre
en Base.metadata. Sin este import, scripts/seed_admin.py (Base.metadata.create_all)
no crearia las tablas de modelos que no se hayan importado en algun lugar.

IMPORTANTE: Media se importa antes que Product porque Product tiene una
llave foranea hacia media.id.
"""

from app.models.user import User  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.media import Media  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.sale import Sale, SaleDetail  # noqa: F401
