from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # --- Project ---
    PROJECT_NAME: str = "Baking E-commerce API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # --- Database ---
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "baking_ecommerce"

    # --- Security ---
    SECRET_KEY: str = "changeme-use-openssl-rand-hex-32-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
