import asyncio
from cloudinary import uploader
import cloudinary
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
    async def upload_image(user_id: int, image_file: UploadFile, folder_name: str = None):
        try:
            if not folder_name:
                folder_name = f"ImageHubProjectDB/user_{user_id}/original_images"

            response = await asyncio.to_thread(cloudinary.uploader.upload, image_file.file,
                                               folder=folder_name)  # type: ignore
            return response['url'], response['public_id']

        except Exception as err:
            CloudService.handle_exceptions(err)

    @staticmethod
    async def delete_picture(public_id: str):
        try:
            await asyncio.to_thread(
                cloudinary.uploader.destroy,
                public_id
            )
        except Exception as err:
            CloudService.handle_exceptions(err)

    @staticmethod
    async def update_cloud_image(public_id: str, transformation_params: dict):
        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, uploader.explicit, public_id, type='upload', eager=[transformation_params])  # noqa

            if 'eager' in response and response['eager']:
                eager_transformed_url = response['eager'][0]['url']
                return eager_transformed_url

        except Exception as err:
            CloudService.handle_exceptions(err)