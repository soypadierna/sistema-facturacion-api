from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    PASSWORD_PEPPER: str
    JWT_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: str = "*"
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_STORAGE_BUCKET: str

    @field_validator("JWT_SECRET")
    @classmethod
    def _check_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("JWT_SECRET debe tener al menos 32 caracteres")
        return v

    @field_validator("PASSWORD_PEPPER")
    @classmethod
    def _check_pepper(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError("PASSWORD_PEPPER debe tener al menos 16 caracteres")
        return v

    @field_validator("SUPABASE_URL")
    @classmethod
    def _strip_supabase_url(cls, v: str) -> str:
        return v.rstrip("/")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"

settings = Settings()