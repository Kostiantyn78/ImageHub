from pathlib import Path

from fastapi import HTTPException, status, Depends
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from pydantic import EmailStr

from src.database.db import get_db
from src.repository.users import get_user_by_email
from src.services.auth import auth_service
from src.conf.config import config


conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="Users System",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to verify their email address.
        The function takes in three parameters:
            -email: the user's email address, which is used as a recipient for the message and also
                included in the token that is sent along with it. This allows us to verify that they are
                who they say they are when clicking on this link. It also allows us to identify them if we need
                to send them another verification link later on (for example, if their first one expires).

    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Pass the username to the template
    :param host: str: Create a link to the verification page
    :return: A coroutine object, which can be awaited
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)
