from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "postgresql+asyncpg://POSTGRES_USER:POSTGRES_PASSWORD@POSTGRES_DOMAIN:5432/POSTGRES_DB"
    SECRET_KEY_JWT: str = "secret_jwt"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "secret@email.ua"
    MAIL_PASSWORD: str = "password"
    MAIL_FROM: str = "secret@email.ua"
    MAIL_PORT: int = 000000
    MAIL_SERVER: str = "email_server"
    CLD_NAME: str = "cloudinary_name"
    CLD_API_KEY: int = 0000000000000
    CLD_API_SECRET: str = "cloudinary_api_secret"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("Algorithm must be HS256 or HS512")
        return v

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
