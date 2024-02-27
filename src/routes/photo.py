from fastapi import APIRouter, Depends, status, Path, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import photos as repo_photos
from src.schemas.photo_valid import ImageSchema, ImageResponseSchema, ImageUpdateSchema
from src.services.auth import auth_service

router = APIRouter(prefix='/images')


@router.get("/{picture_id}", response_model=ImageResponseSchema)
async def get_picture(
        picture_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    """
    The get_picture function returns a picture object from the database.
    The function takes in an integer as a parameter, which is the id of the picture to be returned.
    It also takes in two dependencies: db and user.
        - db is used to connect to our database using SQLAlchemy's sessionmaker() method, which creates sessions
        for us that we can use to query our database with SQLAlchemy's ORM methods (e.g., .query(), .add(), etc.).
        - user is used by FastAPI's auth_service dependency, which uses JWT tokens passed through HTTP requests'
        Authorization

    :param picture_id: int: Specify the picture id
    :param db: AsyncSession: Pass the database session to the function
    :param user: Check if the user is logged in and has access to the picture
    :param : Get the picture id
    :return: A picture and the get_pictures function returns a list of pictures

    """
    picture = await repo_photos.get_picture(picture_id, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return picture


@router.post("/upload_image", response_model=ImageResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_image(
        file: UploadFile = File(...),
        body: ImageSchema = Depends(),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user)
):
    """
    The upload_image function is used to upload an image to the database.

    :param file: UploadFile: Get the file from the request
    :param body: ImageSchema: Validate the data that is passed in
    :param db: AsyncSession: Get the database session
    :param user: User: Get the user that is currently logged in
    :return: A picture object

    """
    try:
        picture = await repo_photos.upload_picture(file, body, db, user)
        if picture is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='SOMETHING WENT WRONG')
        return picture
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An error occurred while processing your request.'
        )


@router.delete("/{picture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
        picture_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    """
    The delete_image function deletes a picture from the database.
    It takes in an integer as a parameter, which is the id of the picture to be deleted.
    The function returns a dictionary containing information about the deleted image.

    :param picture_id: int: Specify the picture id of the image to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: Get the current user
    :param : Get the id of the picture to be deleted
    :return: The deleted picture

    """
    picture = await repo_photos.delete_picture(picture_id, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')
    return picture


@router.patch("/{picture_id}", response_model=ImageResponseSchema)
async def update_image(
        body: ImageUpdateSchema,
        picture_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    """
    The update_image function updates an image in the database.
    The function takes a picture_id and body as input, and returns the updated image.
    If no such image exists, it raises a 404 error.

    :param body: ImageUpdateSchema: Validate the request body
    :param picture_id: int: Get the picture id from the url
    :param db: AsyncSession: Pass the database connection to the function
    :param user: Check if the user is logged in
    :param : Get the id of the image to be deleted
    :return: A picture object

    """
    picture = await repo_photos.image_update(picture_id, body, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return picture
