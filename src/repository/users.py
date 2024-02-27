from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User, Role, Image
from src.schemas.user import UserModel


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
        If no such user exists, it returns None.

    :param email: str: Specify the email of the user we want to retrieve
    :param db: AsyncSession: Pass the database session to the function
    :return: A single user object
    """
    query = select(User).filter_by(email=email)
    user = await db.execute(query)
    user = user.unique().scalar_one_or_none()
    return user


async def create_user(body: UserModel, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Get the user data from the request body
    :param db: AsyncSession: Get the database session
    :return: A user object
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    is_first_user = await check_is_first_user(db)
    if is_first_user:
        new_user = User(**body.model_dump(),
                        avatar=avatar, role=Role.admin)
    else:
        new_user = User(**body.model_dump(), avatar=avatar)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def check_is_first_user(db: AsyncSession):
    """
    The check_is_first_user function checks if the user is the first user in the database.
        If so, it returns True. Otherwise, it returns False.

    :param db: AsyncSession: Pass the database session to the function
    :return: True if the user table is empty, false otherwise
    """
    query = select(func.count()).select_from(User)
    result = await db.execute(query)
    return result.unique().scalar() == 0


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Specify the user that we want to update
    :param token: str | None: Update the refresh token of a user
    :param db: AsyncSession: Pass the database session to the function
    :return: The user object
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession):
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Get the email of the user
    :param db: AsyncSession: Pass the database session to the function
    :return: A boolean value
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar url of a user.

    :param email: str: Identify the user in the database
    :param url: str | None: Specify that the url parameter can be a string or none
    :param db: AsyncSession: Pass in the database session
    :return: A user object, which is the same as what we get from the get_user_by_email function
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_username function takes a username and returns the user object associated with that username.
        If no such user exists, it returns None.

    :param username: str: Pass the username of the user to be retrieved
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object if the username exists in the database
    """
    query = select(User).filter_by(username=username)
    user = await db.execute(query)
    user = user.unique().scalar_one_or_none()
    return user


async def get_count_photo(db: AsyncSession, user: User):
    """
    The get_count_photo function is used to update the count_photo attribute of a user.
        The function takes in an async database session and a User object as parameters.
        It then queries the Image table for all images that have been uploaded by the user,
        and counts how many unique images there are (i.e., if two users upload the same image,
        it will only be counted once). If no images are found, then count_photo is set to 1; otherwise,
        it is set equal to len(images), which returns how many unique photos were uploaded by that user.

    :param db: AsyncSession: Connect to the database
    :param user: User: Get the user object from the database
    :return: The number of images uploaded by the user
    """
    query = select(Image).filter_by(user=user)
    images = await db.execute(query)

    if images is None:
        count_photo = 1
    else:
        count_photo = len(images.unique().all())

    user.count_photo = count_photo
    await db.commit()
    await db.refresh(user)
