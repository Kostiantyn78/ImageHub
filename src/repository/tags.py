from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Tag


async def get_or_create_tag(tag_name: str, db: AsyncSession):
    """
    The get_or_create_tag function takes a tag name and an async database session as arguments.
    It then checks to see if the tag already exists in the database, and returns it if so.
    If not, it creates a new Tag object with that name, adds it to the session, commits
    the changes to the database (which will create a new row), refreshes our local copy of
    the object from what's in the DB (to get its ID), and returns that.

    :param tag_name: str: Pass in the name of the tag to be created
    :param db: AsyncSession: Pass in the database session
    :return: A tag object
    """
    existing_tag = await db.execute(select(Tag).where(Tag.name == tag_name))
    existing_tag = existing_tag.unique().scalar_one_or_none()

    if existing_tag:
        return existing_tag

    new_tag = Tag(name=tag_name)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)

    return new_tag
