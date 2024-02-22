import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserResponse, UserProfile
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users


router = APIRouter(prefix="/users", tags=["Users"])

cloudinary.config(cloud_name=config.CLOUDINARY_NAME, api_key=config.CLOUDINARY_API_KEY,
                  api_secret=config.CLOUDINARY_API_SECRET, secure=True)


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user),
                        db: AsyncSession = Depends(get_db)):
    public_id = f"avatar/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)

    res_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop="fill",
                                                              version=res.get("version"))
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    return user


@router.get("/{username}", response_model=UserProfile)
async def get_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    user_profile = await repositories_users.get_user_by_username(username, db)
    await repositories_users.get_count_photo(db, user_profile)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user_profile
