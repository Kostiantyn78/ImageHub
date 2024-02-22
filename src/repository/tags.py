from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Tag


async def get_or_create_tag(tag_name: str, db: AsyncSession):
    existing_tag = await db.execute(select(Tag).where(Tag.name == tag_name))
    existing_tag = existing_tag.unique().scalar_one_or_none()

    if existing_tag:
        return existing_tag

    new_tag = Tag(name=tag_name)
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)

    return new_tag
