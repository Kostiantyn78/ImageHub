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
    picture = await repo_photos.image_update(picture_id, body, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return picture
