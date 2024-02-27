import asyncio
from io import BytesIO

from cloudinary import uploader
import cloudinary
from PIL import Image
from cloudinary.exceptions import Error as CloudinaryError
from fastapi import HTTPException, UploadFile
from requests import TooManyRedirects
from requests.exceptions import RequestException, Timeout, HTTPError

from src.conf.config import config

cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
)


class CloudService:
    @staticmethod
    def handle_exceptions(err):
        """
        The handle_exceptions function is a custom exception handler that will catch any exceptions
        that are raised by the cloudinary_upload function and return an appropriate HTTP response.
        This allows us to handle errors in a consistent way across our application.

        :param err: Catch the error that is raised by the function
        :return: An httpexception
        """
        if isinstance(err, CloudinaryError):
            raise HTTPException(status_code=500, detail=f"Cloudinary API error: {err}")
        elif isinstance(err, RequestException):
            raise HTTPException(status_code=500, detail=f"Ops something get wrong: {err}")
        elif isinstance(err, Timeout):
            raise HTTPException(status_code=500, detail=f"Request timed out: {err}")
        elif isinstance(err, TooManyRedirects):
            raise HTTPException(status_code=500, detail=f"Too many redirects: {err}")
        elif isinstance(err, HTTPError):
            if err.response.status_code == 401:
                raise HTTPException(status_code=401, detail=f"Unauthorized: {err}")
            elif err.response.status_code == 400:
                raise HTTPException(status_code=400, detail=f"Bad request: {err}")
            else:
                raise HTTPException(status_code=500, detail=f"HTTP error: {err}")
        elif isinstance(err, IOError):
            raise HTTPException(status_code=500, detail=f"I/O error: {err}")
        elif isinstance(err, FileNotFoundError):
            raise HTTPException(status_code=404, detail=f"File not found: {err}")
        else:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {err}")

    @staticmethod
    async def upload_image(user_id: int, image_file: UploadFile, folder_path: str = None):
        """
        The upload_image function uploads an image to the cloudinary server.
            Args:
                user_id (int): The id of the user who uploaded the image.
                image_file (UploadFile): The file object containing information about
                    the uploaded file, such as its name and size. This is a type defined by FastAPI.

        :param user_id: int: Create a folder for each user in the cloudinary database
        :param image_file: UploadFile: Upload the image file to cloudinary
        :param folder_path: str: Specify the folder in which the image will be uploaded to
        :return: A tuple of the image url and public_id
        """
        try:
            if not folder_path:
                folder_path = f"ImageHubProjectDB/user_{user_id}/original_images"

            response = await asyncio.to_thread(cloudinary.uploader.upload, image_file.file,
                                               folder=folder_path)  # type: ignore
            return response['url'], response['public_id']

        except Exception as err:
            CloudService.handle_exceptions(err)

    @staticmethod
    async def delete_picture(public_id: str):
        """
        The delete_picture function is used to delete a picture from the Cloudinary cloud storage service.
            It takes in one parameter, public_id, which is the unique identifier of the image that will be deleted.
            The function uses asyncio and cloudinary to delete an image with a given public_id.

        :param public_id: str: Identify the picture to be deleted
        :return: A dictionary with the following keys:
        """
        try:
            await asyncio.to_thread(
                cloudinary.uploader.destroy,
                public_id
            )
        except Exception as err:
            CloudService.handle_exceptions(err)

    @staticmethod
    async def upload_transformed_image(user_id: int, image_url: str, params_of_transform: dict):
        """
        The upload_transformed_image function uploads an image to the Cloudinary cloud service,
        transforms it according to the parameters passed in as a dictionary, and returns its URL.


        :param user_id: int: Identify the user in the database
        :param image_url: str: Specify the image to be transformed
        :param params_of_transform: dict: Pass the transformation parameters to the cloudinary
        :return: The url of the uploaded image and its public_id
        """
        try:
            folder_path = f"ImageHubProjectDB/user_{user_id}/transformed_images"
            response = await asyncio.to_thread(cloudinary.uploader.upload, image_url,
                                               transformation=params_of_transform, folder=folder_path)  # noqa

            return response['url'], response['public_id']

        except Exception as err:
            CloudService.handle_exceptions(err)

    @staticmethod
    async def update_image_on_cloudinary(cloudinary_public_id: str, params_of_transform: dict):
        """
        The update_image_on_cloudinary function is used to update an image on Cloudinary.
            It takes in a cloudinary_public_id and params_of_transform as arguments, and returns the url of the transformed image.
            The function uses asyncio to run the cloudinary uploader explicit method in a thread, which updates an existing
            resource with new parameters (eager transformation). If successful, it returns the eager transformed url.

        :param cloudinary_public_id: str: Identify the image in cloudinary
        :param params_of_transform: dict: Specify the transformation parameters
        :return: The url of the transformed image
        """
        try:
            response = await asyncio.to_thread(cloudinary.uploader.explicit, cloudinary_public_id,
                                               type='upload', eager=[params_of_transform])  # noqa

            if 'eager' in response and response['eager']:
                eager_transformed_url = response['eager'][0]['url']
                return eager_transformed_url

        except Exception as err:
            CloudService.handle_exceptions(err)

    @staticmethod
    async def upload_qr_code(user_id: int, img: Image.Image):
        """
        The upload_qr_code function uploads a QR code image to the cloudinary server.
            The function takes in two parameters: user_id and img.
            The user_id parameter is an integer that represents the id of the user who's QR code is being uploaded.
            The img parameter is an Image object that represents the QR code image to be uploaded.

        :param user_id: int: Specify the user's id
        :param img: Image.Image: Specify the image that is to be uploaded
        :return: A tuple of the url and public_id
        """
        try:
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            folder_path = f"ImageHubProjectDB/user_{user_id}/qr_codes"
            response = await asyncio.to_thread(cloudinary.uploader.upload, buffer, folder=folder_path)  # noqa
            return response['url'], response['public_id']

        except Exception as err:
            CloudService.handle_exceptions(err)
