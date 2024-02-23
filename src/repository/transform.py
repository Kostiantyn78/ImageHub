import qrcode
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.entity.models import Transform, Image

from src.services.cloud_service import CloudService


class TransformRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transformed_image(self, user_id: int, natural_photo_id: int,
                                       params_of_transform: dict):
        initial_photo = await self.get_image_by_id(natural_photo_id)
        if not initial_photo:
            return None
        try:
            transformed_url, cloudinary_public_id = await CloudService.upload_transformed_image(
                user_id, initial_photo.url, params_of_transform)
            qr_image = qrcode.make(transformed_url)
            qr_code_url, qr_code_public_id = await CloudService.upload_qr_code(user_id, qr_image)
            transformed_image = Transform(
                natural_photo_id=natural_photo_id,
                image_url=transformed_url,
                cloudinary_public_id=cloudinary_public_id,
                qr_code_url=qr_code_url,
                qr_code_public_id=qr_code_public_id,
                user_id=user_id,
            )
            self.session.add(transformed_image)
            await self.session.commit()
            await self.session.refresh(transformed_image)
            return transformed_image
        except Exception as err:
            print(f"Error in create_transformed_image: {err}")
            await self.session.rollback()  # do rollback if an error occurs
            return None

    async def update_transformed_image(self, transformed_image_id: int, params_of_transform: dict):
        transformed_image = await self.get_transformed_image(transformed_image_id)
        user_id = transformed_image.user_id
        if not transformed_image:
            return None
        try:
            new_transformed_url = await CloudService.update_image_on_cloudinary(
                cloudinary_public_id=transformed_image.cloudinary_public_id,
                params_of_transform=params_of_transform
            )
            if not new_transformed_url:
                return None
            new_qr_image = qrcode.make(new_transformed_url)
            new_qr_url, new_qr_public_id = await CloudService.upload_qr_code(user_id, new_qr_image)
            transformed_image.url = new_transformed_url
            transformed_image.qr_url = new_qr_url
            transformed_image.qr_public_id = new_qr_public_id
            self.session.add(transformed_image)
            await self.session.commit()
            await self.session.refresh(transformed_image)
            return transformed_image
        except Exception:
            return None

    async def get_image_by_id(self, images_id: int):
        query = select(Image).where(Image.id == images_id)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_transformed_image(self, transformed_image_id: int):
        query = select(Transform).where(Transform.id == transformed_image_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_transforms_by_user_id(self, user_id: int):
        query = select(Transform).where(Transform.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def delete_transformed_image(self, transformed_image_id: int):
        query = select(Transform).where(Transform.id == transformed_image_id)
        result = await self.session.execute(query)
        transformed_image = result.scalars().first()
        if transformed_image:
            try:
                await CloudService.delete_picture(transformed_image.cloudinary_public_id)
                await CloudService.delete_picture(transformed_image.qr_code_public_id)
                await self.session.delete(transformed_image)
                await self.session.commit()
            except HTTPException as http_error:
                raise HTTPException(status_code=http_error.status_code, detail=http_error.detail)
            except Exception as error:
                await self.session.rollback()
                raise HTTPException(status_code=500, detail=f"Internal Server Error: {error}")
            return True
        return False
