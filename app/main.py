import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api import auth, users, dashboard, categories, products, sales, reports, media

app = FastAPI(
    title="Sistema Web de Inventario y Ventas",
    description="API para administrar inventario, ventas y reportes.",
    version="0.1.0",
)

# En produccion, ALLOWED_ORIGINS en el .env debe apuntar a la URL real del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(sales.router)
app.include_router(reports.router)
app.include_router(media.router)

# Sirve las imagenes subidas (ej: /uploads/products/archivo.jpg)
os.makedirs(os.path.join(settings.UPLOADS_DIR, "products"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOADS_DIR, "users"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOADS_DIR, "guides"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")


@app.get("/api/health", tags=["Sistema"])
def health_check():
    return {"success": True, "message": "API funcionando correctamente"}
