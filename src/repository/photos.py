from typing import List

from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Image, User, Role, Tag
from src.repository import tags as repo_tags
from src.schemas.photo_valid import ImageSchema, ImageUpdateSchema

from src.services.cloud_service import CloudService


async def has_access(user: User, photo_owner, status_role):
    """
    The has_access function checks if a user has access to a photo.

    :param user: User: Get the user's id
    :param photo_owner: Check if the user is the owner of a photo
    :param status_role: Determine if the user is an admin or not
    :return: True if the user is either the photo owner or an admin
    """
    return user.id == photo_owner or status_role == Role.admin


async def get_picture(picture_id: int, db: AsyncSession, user: User):
    """
    The get_picture function returns a picture object with the following fields:
        - user_id: The id of the user who created this picture.
        - picture_id: The id of this specific image.
        - url: A URL to access the image file itself. This is not stored in our database, but rather on an external service like AWS S3 or Google Cloud Storage (GCS). We will use GCS for this project, and you can read more about it here https://cloud.google.com/storage/docs/. You do not need to worry about setting up your own GCS bucket; we have already

    :param picture_id: int: Specify the picture id
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Check if the user has access to the picture
    :return: A dictionary with the following keys:
    """
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
    """
    The process_tags function takes a string of comma-separated tags and returns a list of Tag objects.

    :param tags_str: str: Get the tags from the request body
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of tag objects
    """
    tags = [tag.strip() for tag in tags_str.split(',')]
    if len(tags) > 5:
        raise ValueError("You can add up to 5 tags")
    tag_objects = []
    for tag in tags:
        result = await repo_tags.get_or_create_tag(tag, db)
        tag_objects.append(result)
    return tag_objects


async def upload_picture(file: UploadFile, body: ImageSchema, db: AsyncSession, user: User) -> dict:
    """
    The upload_picture function is used to upload a picture to the database.

    :param file: UploadFile: Get the file from the request
    :param body: ImageSchema: Validate the request body
    :param db: AsyncSession: Access the database
    :param user: User: Get the user id of the user that is uploading a picture
    :return: A dictionary with the following keys:
    """
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
    """
    The delete_picture function deletes a picture from the database and cloudinary.
        Args:
            picture_id (int): The id of the image to be deleted.
            db (AsyncSession): A connection to the database.  This is provided by FastAPI's dependency injection system, which we will learn more about later in this course.  For now, just know that you need to include it as an argument in your function definition for it to work properly!
            user (User): The currently logged-in user object, also provided by FastAPI's dependency injection system

    :param picture_id: int: Specify the picture to be deleted
    :param db: AsyncSession: Access the database
    :param user: User: Check if the user has access to delete the picture
    :return: A string, which is the response body
    """
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
    """
    The image_update function updates the description of an image.

    :param picture_id: int: Get the picture id from the url
    :param body: ImageUpdateSchema: Validate the request body
    :param db: AsyncSession: Make the database connection available to the function
    :param user: User: Check if the user has access to delete the picture
    :return: A dictionary with the updated picture information
    """
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
