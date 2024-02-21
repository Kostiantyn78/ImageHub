from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User, Role, Image
from src.schemas.user import UserModel


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    query = select(User).filter_by(email=email)
    user = await db.execute(query)
    user = user.unique().scalar_one_or_none()
    return user


async def create_user(body: UserModel, db: AsyncSession = Depends(get_db)):
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
    query = select(func.count()).select_from(User)
    result = await db.execute(query)
    return result.unique().scalar() == 0


async def update_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession):
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    query = select(User).filter_by(username=username)
    user = await db.execute(query)
    user = user.unique().scalar_one_or_none()
    return user


async def get_count_photo(db: AsyncSession, user: User):
    query = select(Image).filter_by(user=user)
    images = await db.execute(query)

    if images is None:
        count_photo = 1
    else:
        count_photo = len(images.unique().all())

    user.count_photo = count_photo
    await db.commit()
    await db.refresh(user)
