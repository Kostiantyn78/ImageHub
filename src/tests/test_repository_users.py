import pytest
import unittest
from unittest.mock import patch, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User, Image
from src.repository.users import create_user, update_token, confirmed_email, update_avatar_url, get_count_photo
from src.schemas.user import UserModel


class TestUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        """
        The setUp function is called before each test function.
        It creates a new AsyncMock object for the session, and a User object with some attributes.

        :param self: Represent the instance of the class
        :return: A user object with the following attributes:
        """
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, username='test_user', password="qwerty", email='test@example.com')

    @patch('src.repository.users.Gravatar', spec=True)
    @patch('src.repository.users.User', spec=True)
    async def test_create_user_success(self, MockUser, MockGravatar):
        """
        The test_create_user_success function tests the create_user function.

        :param self: Represent the instance of the class
        :param MockUser: Mock the user class from the src
        :param MockGravatar: Mock the gravatar class
        :return: The created_user variable, which is the result of calling create_user with the user data and mock
        database session
        """
        mock_db_session = AsyncMock()
        mock_gravatar_instance = MockGravatar.return_value
        mock_gravatar_instance.get_image.return_value = 'http://example.com/avatar.jpg'

        user_data = UserModel(email='test@example.com', username='Test User', password='Password')
        mock_user_instance = MockUser.return_value = User(**user_data.model_dump(),
                                                          avatar='http://example.com/avatar.jpg')
        mock_user_instance.email = user_data.email
        mock_user_instance.username = user_data.username
        mock_user_instance.avatar = 'http://example.com/avatar.jpg'

        mock_select_result = AsyncMock()
        mock_select_result.scalar.return_value = 1
        mock_db_session.scalar = mock_select_result

        with patch('src.repository.users.check_is_first_user', return_value=True):
            created_user = await create_user(user_data, mock_db_session)

        mock_db_session.add.assert_called_once_with(mock_user_instance)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_user_instance)

        self.assertEqual(created_user.email, user_data.email)
        self.assertEqual(created_user.username, user_data.username)
        self.assertEqual(created_user.avatar, 'http://example.com/avatar.jpg')

    @patch('src.repository.users.Gravatar', spec=True)
    @patch('src.repository.users.User', spec=True)
    async def test_create_user_with_gravatar_error(self, MockUser, MockGravatar):
        """
        The test_create_user_with_gravatar_error function tests the create_user function when a Gravatar error occurs.

        :param self: Access the instance of the class
        :param MockUser: Mock the user class
        :param MockGravatar: Mock the gravatar class
        :return: An exception
        """
        mock_db_session = self.session
        mock_gravatar_instance = MockGravatar.return_value
        mock_gravatar_instance.get_image.side_effect = Exception('Gravatar error')

        user_data = UserModel(email='test@example.com',
                              username='Test User', password='Password')
        mock_user_instance = MockUser.return_value = User(
            **user_data.model_dump(), avatar='http://example.com/avatar.jpg')
        mock_user_instance.email = 'test@example.com'
        mock_user_instance.username = 'Test User'

        with self.assertRaises(Exception):
            await create_user(user_data, mock_db_session)
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()

    @patch('src.repository.users.User', spec=True)
    @pytest.mark.asyncio
    async def test_update_token(self, Mock_User):
        """
        The test_update_token function tests the update_token function.
        It does this by creating a mock user object and passing it to the update_token function, along with a new token
        string.
        The test then asserts that the refresh token of the mock user is equal to 'new token'.  It also asserts that
        session.commit() was called once.

        :param self: Access the attributes and methods of the class
        :param Mock_User: Mock the user class
        :return: The new token
        """
        mock_user = Mock_User.return_value
        token = 'new token'
        await update_token(mock_user, token, self.session)
        self.assertEqual(token, mock_user.refresh_token)
        self.session.commit.assert_called_once()

    @patch('src.repository.users.User', spec=True)
    @pytest.mark.asyncio
    async def test_confirmed_email(self, MockUser):
        """
        The test_confirmed_email function tests the confirmed_email function in the users repository.

        :param self: Access the class that the test function is defined in
        :param MockUser: Create a mock user object
        :return: True if the user's confirmed attribute is set to true
        """
        # Create a mock database session
        mock_db_session = AsyncMock()

        # Create a mock user
        mock_user = MockUser.return_value
        mock_user.email = 'test@example.com'

        # Mock the get_user_by_email function
        with patch('src.repository.users.get_user_by_email', return_value=mock_user) as mock_get_user:
            # Test the function
            await confirmed_email('test@example.com', mock_db_session)

            # Check that get_user_by_email was called with the correct parameters
            mock_get_user.assert_called_once_with('test@example.com', mock_db_session)

            # Check that the user was saved with the confirmed attribute set to True
            assert mock_user.confirmed is True

    @pytest.mark.asyncio
    async def test_update_avatar_url(self):
        """
        The test_update_avatar_url function tests the update_avatar_url function.

        :param self: Refer to the class that is being tested
        :return: The user object, which is the same as the mock_user object
        """
        # Create a mock database session
        mock_db_session = Mock(spec=AsyncSession)

        # Create a mock user
        mock_user = Mock(spec=User)
        mock_user.email = 'test@example.com'

        # Mock the get_user_by_email function
        with patch('src.repository.users.get_user_by_email', return_value=mock_user) as mock_get_user:
            # Test the function
            updated_user = await update_avatar_url('test@example.com', 'new_avatar_url', mock_db_session)

            # Check that get_user_by_email was called with the correct parameters
            mock_get_user.assert_called_once_with('test@example.com', mock_db_session)

            # Check that the avatar attribute of the user was updated
            assert mock_user.avatar == 'new_avatar_url'

            # Check that the commit method was called on the database
            mock_db_session.commit.assert_called_once()

            # Check that the refresh method was called on the database with the user object
            mock_db_session.refresh.assert_called_once_with(mock_user)

            # Check that the expected user is returned
            assert updated_user == mock_user
