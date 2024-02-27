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
        """
        The create_transformed_image function takes in a user_id, natural_photo_id, and params of transform.
        It then uses the get image by id function to retrieve the initial photo from the database. If it is not found,
        it returns None. It then uploads a transformed image using CloudService's upload transformed image function and
        returns its url and cloudinary public id as well as creating a QR code for that url using CloudService's
        upload qr code function which also returns its url and cloudinary public id. It creates an instance of Transform
        with all these values along with user_id (which was

        :param self: Represent the instance of the class
        :param user_id: int: Identify the user who is uploading the image
        :param natural_photo_id: int: Get the image from the database
        :param params_of_transform: dict: Pass in the transformation parameters to be used by cloudinary
        :return: A transform object, which is a database model
        """
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
        """
        The update_transformed_image function takes in a transformed_image_id and params_of_transform.
        It then gets the transformed image from the database using get_transformed image, which returns None if it doesn't exist.
        If it does exist, we update the cloudinary public id with new parameters of transform (which is a dictionary).
        We then create a new QR code for this updated url and upload that to Cloudinary as well. We add all these changes to our database session, commit them, refresh them so they are up-to-date with what's in our database now (and not just what was there when we started

        :param self: Access the attributes and methods of the class
        :param transformed_image_id: int: Get the transformed image from the database
        :param params_of_transform: dict: Update the image on cloudinary
        :return: The transformed_image object
        """
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
        """
        The get_image_by_id function takes in an image id and returns the corresponding image object.

        :param self: Represent the instance of a class
        :param images_id: int: Select the image with a specific id
        :return: The image with the given id
        """
        query = select(Image).where(Image.id == images_id)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_transformed_image(self, transformed_image_id: int):
        """
        The get_transformed_image function takes in a transformed_image_id and returns the corresponding
        transformed image. The function uses an SQLAlchemy query to select the Transform object with the
        given id, then executes that query using await self.session.execute(query). Finally, it returns
        the first result of that execution.

        :param self: Represent the instance of a class
        :param transformed_image_id: int: Identify the image that is being transformed
        :return: A transformed image object
        """
        query = select(Transform).where(Transform.id == transformed_image_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_transforms_by_user_id(self, user_id: int):
        """
        The get_transforms_by_user_id function returns a list of all transforms for the user with the given id.

        :param self: Represent the instance of a class
        :param user_id: int: Select the user_id from the transform table
        :return: All unique transforms for a user
        """
        query = select(Transform).where(Transform.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def delete_transformed_image(self, transformed_image_id: int):
        """
        The delete_transformed_image function deletes a transformed image from the database and cloudinary.
            Args:
                transformed_image_id (int): The id of the transformed image to be deleted.

        :param self: Represent the instance of the class
        :param transformed_image_id: int: Specify which transformed image to delete
        :return: A boolean value
        """
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
