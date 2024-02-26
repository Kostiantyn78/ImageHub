import asyncio
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import cloudinary
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.entity.models import User, Role, Image
from src.repository.photos import has_access, get_picture, upload_picture, delete_picture
from src.schemas.photo_valid import ImageSchema


class TestHasAccess(unittest.IsolatedAsyncioTestCase):

    """Test cases for the has_access function."""

    async def test_has_access_admin(self):

        """Test has_access function when the user is an admin."""

        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, role=Role.admin)
        self.photo_owner = 1
        self.status_role = Role.admin

        result = await has_access(self.user, self.photo_owner, self.status_role)

        self.assertTrue(result)

    async def test_has_access_user_id_match(self):

        """Test has_access function when user ID matches the photo owner."""

        self.user = User(id=1, role=Role.user)
        self.photo_owner = 1
        self.status_role = Role.user

        result = await has_access(self.user, self.photo_owner, self.status_role)

        self.assertTrue(result)

    async def test_has_access_user_id_not_match(self):

        """Test has_access function when user ID does not match the photo owner."""

        self.user = User(id=2, role=Role.user)
        self.photo_owner = 1
        self.status_role = Role.user

        self.result = await has_access(self.user, self.photo_owner, self.status_role)

        self.assertFalse(self.result)


class TestPhoto(unittest.IsolatedAsyncioTestCase):

    """Test cases for photo-related functions: get_picture, upload_picture, delete_picture."""

    def setUp(self) -> None:

        """Set up common objects and data for test cases."""

        self.session = AsyncMock(spec=AsyncSession)
        self.image = Image(id=1, url='url ImageHUB', description='ImageHUB',
                           created_at=datetime(2000, 3, 12), updated_at=datetime(2000, 3, 13))
        self.images = [
            self.image,
            Image(
                id=2,
                url=self.image.url,
                description=self.image.description,
                created_at=self.image.created_at,
                updated_at=self.image.updated_at
            ),
            Image(
                id=3,
                url=self.image.url,
                description=self.image.description,
                created_at=self.image.created_at,
                updated_at=self.image.updated_at
            )
        ]

    async def test_get_image(self):

        """Test get_picture function for fetching an image."""

        mocked_image = MagicMock()
        mocked_image.scalar_one_or_none.return_value = self.image
        self.session.execute.return_value = mocked_image
        try:
            result = await get_picture(1, self.session, User())
            self.assertIsNotNone(result, 'Picture object is None')
        except HTTPException as e:
            self.assertEqual(e.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(e.detail, 'Not enough permissions')

    async def test_upload_picture_success(self):

        """Test upload_picture function for successful image upload."""

        with patch("src.services.cloud_service.CloudService.upload_image") as mock_upload_image:
            mock_upload_image.return_value = ("mocked_url", "mocked_public_id")

            file = UploadFile(filename="open_check.png", file=True)  # type: ignore
            body = ImageSchema(
                user_id=1,
                picture_id=1,
                url="url ImageHUB",
                description="Test ImageHUB",
                created_at=datetime(2022, 2, 26),
            )
            db_session = AsyncMock(spec=AsyncSession)
            user = User(id=1)

            result = await upload_picture(file, body, db_session, user)

            self.assertEqual(result['user_id'], 1)
            self.assertEqual(result['url'], 'mocked_url')
            self.assertEqual(result['description'], 'Test ImageHUB')

            await asyncio.gather()

    @patch("src.services.cloud_service.CloudService.delete_picture")
    async def test_delete_image(self, mock_delete_picture):

        """Test delete_picture function for deleting an image."""

        cloudinary.config(
            cloud_name=config.CLOUDINARY_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
        )

        mocked_image = MagicMock()
        mocked_image.scalar_one_or_none.return_value = self.image
        self.session.execute.return_value = mocked_image

        with patch("src.repository.photos.has_access", return_value=True):
            result = await delete_picture(picture_id=1, db=self.session, user=User())

        self.assertEqual(result, 'Success')

    from unittest.mock import patch

    @patch("src.services.cloud_service.CloudService.delete_picture")
    async def test_delete_image_not_found(self, mock_delete_picture):

        """Test delete_picture function when the specified image is not found."""

        cloudinary.config(
            cloud_name=config.CLOUDINARY_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET,
        )
        mocked_image = MagicMock()
        mocked_image.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_image

        user = User(id=1, username="user ImageHUB", password="ImageHUB", email="test@example.com")

        with patch("src.repository.photos.has_access", return_value=True):
            result = await delete_picture(picture_id=16, db=self.session, user=user)

        self.assertEqual(result, 'Success')


if __name__ == "__main__":
    unittest.main()
