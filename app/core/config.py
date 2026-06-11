from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:admin@localhost:5432/FoodStoreApi"
    JWT_SECRET: str = "supersecretkeyquecambiarenproduccion"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BCRYPT_COST: int = 12
    COOKIE_DOMAIN: str | None = None
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

settings = Settings()