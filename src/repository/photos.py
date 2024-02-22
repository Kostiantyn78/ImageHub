from typing import List

from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Image, User, Role, Tag
from src.repository import tags as repo_tags
from src.schemas.photo_valid import ImageSchema, ImageUpdateSchema

from src.services.cloud_service import CloudService


async def has_access(user: User, photo_owner, status_role):
    return user.id == photo_owner or status_role == Role.admin


async def get_picture(picture_id: int, db: AsyncSession, user: User):
    stmt = select(Image).where(Image.id == picture_id)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    if picture:
        if not await has_access(user, picture.user_id, user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Not enough permissions'
            )

        result = {
            'user_id': picture.user_id,
            'picture_id': picture.id,
            'url': picture.url,
            'description': picture.description,
            'tags': [tag.name for tag in picture.tags],
            'created_at': picture.created_at,
        }
        return result
    return picture


async def process_tags(tags_str: str, db: AsyncSession) -> List[Tag]:
    tags = [tag.strip() for tag in tags_str.split(',')]
    if len(tags) > 5:
        raise ValueError("You can add up to 5 tags")
    tag_objects = []
    for tag in tags:
        result = await repo_tags.get_or_create_tag(tag, db)
        tag_objects.append(result)
    return tag_objects


async def upload_picture(file: UploadFile, body: ImageSchema, db: AsyncSession, user: User) -> dict:
    image_data = await CloudService.upload_image(user.id, file)
    if image_data is None:
        return {"detail": "Image upload failed", "status_code": status.HTTP_400_BAD_REQUEST}

    image_url, public_id = image_data
    picture = Image(url=image_url, description=body.description, cloudinary_public_id=public_id, user_id=user.id)

    if body.tags:
        try:
            tag_objects = await process_tags(body.tags, db)
            picture.tags.extend(tag_objects)
        except ValueError as e:
            await CloudService.delete_picture(public_id)
            return {"detail": str(e), "status_code": status.HTTP_400_BAD_REQUEST}

    db.add(picture)
    await db.commit()
    await db.refresh(picture)

    return {
        'user_id': picture.user_id,
        'picture_id': picture.id,
        'url': picture.url,
        'description': picture.description,
        'tags': [tag.name for tag in picture.tags],
        'created_at': picture.created_at,
    }


async def delete_picture(picture_id: int, db: AsyncSession, user: User):
    picture = await db.get(Image, picture_id)

    if not picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )

    if not await has_access(user, picture.user_id, user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Access forbidden'
        )

    try:
        await CloudService.delete_picture(picture.cloudinary_public_id)
        await db.delete(picture)
        await db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting picture"
        )

    return 'Success'


async def image_update(picture_id: int, body: ImageUpdateSchema, db: AsyncSession, user: User):
    stmt = select(Image).where(Image.id == picture_id)
    result = await db.execute(stmt)
    picture = result.unique().scalar_one_or_none()

    if not picture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found"
        )

    if not await has_access(user, picture.user_id, user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Access forbidden'
        )

    try:
        picture.description = body.description
        await db.commit()
        await db.refresh(picture)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating picture"
        )

    return {
        'user_id': picture.user_id,
        'picture_id': picture.id,
        'url': picture.url,
        'description': picture.description,
        'tags': [tag.name for tag in picture.tags],
        'created_at': picture.created_at,
    }
