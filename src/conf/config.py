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
    CLOUDINARY_NAME: str = "cloudinary_name"
    CLOUDINARY_API_KEY: int = 0000000000000
    CLOUDINARY_API_SECRET: str = "cloudinary_api_secret"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        """
        The validate_algorithm function is a custom validator that will be used to validate the algorithm field.
        It checks if the value of algorithm is either HS256 or HS512, and raises an error otherwise.

        :param cls: Pass the class of the object being validated
        :param v: Any: Indicate that the function will accept any type of value
        :return: The value of the algorithm
        """
        if v not in ["HS256", "HS512"]:
            raise ValueError("Algorithm must be HS256 or HS512")
        return v

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
