from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuracion central del proyecto.
    Todos los valores sensibles se leen desde el archivo .env
    (nunca se deben hardcodear en el codigo).
    """

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    ADMIN_NAME: str = "Administrador"
    ADMIN_EMAIL: str = "admin@keylita.com"
    ADMIN_PASSWORD: str = "CambiaEsta123"

    # Umbral de unidades para considerar "stock bajo" (⚠️) en productos
    STOCK_BAJO_UMBRAL: int = 5

    # Subida de imagenes de productos
    UPLOADS_DIR: str = "uploads"
    MAX_UPLOAD_MB: int = 5

    # CORS: dominios permitidos a consumir la API, separados por coma.
    # En desarrollo local se deja "*" (cualquier origen). En produccion,
    # se debe restringir a la URL real del frontend (ej: Vercel).
    ALLOWED_ORIGINS: str = "*"

    @property
    def allowed_origins_list(self) -> list[str]:
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
