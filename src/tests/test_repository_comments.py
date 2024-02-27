import unittest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Comment, User
from src.schemas.comment import CommentSchema
from src.repository.comments import create_comment, get_comments, update_comment, delete_comment


class TestAsyncComment(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        """
        The setUp function is called before each test function.
        It creates a new user and session object for each test.

        :param self: Represent the instance of the class
        :return: None, so the test should fail
        """
        self.user = User(
            id=1,
            username='test_user',
            password='test_password',
            confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_comments(self):
        """
        The test_get_comments function tests the get_comments function in the comments.py file.
        It does this by creating a mocked session object, and then using that to mock out the
        return value of self.session.execute(). The mocked return value is a list of three Comment objects, which are then returned from get_comments() and compared against what was expected.

        :param self: Refer to the object itself
        :return: A list of comments
        """
        limit = 10
        offset = 0
        comments = [Comment(id=1, user_id=1, image_id=1, text='Test comment 1',
                            created_at=datetime(2024, 2, 24), updated_at=datetime(2024, 2, 24)),
                    Comment(id=2, user_id=1, image_id=1, text='Test comment 2',
                            created_at=datetime(2024, 2, 24), updated_at=datetime(2024, 2, 24)),
                    Comment(id=3, user_id=1, image_id=1, text='Test comment 3',
                            created_at=datetime(2024, 2, 24), updated_at=datetime(2024, 2, 24))]
        mocked_comments = MagicMock()
        mocked_comments.scalars.return_value.all.return_value = comments
        self.session.execute.return_value = mocked_comments
        result = await get_comments(1, limit, offset, self.session)
        self.assertEqual(result, comments)

    async def test_create_comment(self):
        """
        The test_create_comment function tests the create_comment function in the comments.py file.
        It creates a comment with text 'Test comment 4' and assigns it to post 1, which is created by user 2 (self.user).
        The test checks that result is an instance of Comment and that its text attribute matches body's text attribute.

        :param self: Access the class attributes and methods
        :return: A comment object
        """
        body = CommentSchema(text='Test comment 4')
        result = await create_comment(body, 1, self.session, self.user)
        self.assertIsInstance(result, Comment)
        self.assertEqual(result.text, body.text)

    async def test_update_comment(self):
        """
        The test_update_comment function tests the update_comment function in the comments.py file.
        The test_update_comment function is a coroutine that takes in self as an argument and returns nothing.
        The test_update_comment function creates a body variable that contains CommentSchema(text='Test update comment 1').
        It then creates a mocked comment object called mocked_comment, which has its scalar one or none method return value set to
        Comment(id=2, user id=2, image id=2, text='Test comment 2', created at = datetime(2024, 2, 24), updated at =

        :param self: Represent the instance of the object that is passed to the method when it is called
        :return: An instance of comment
        """
        body = CommentSchema(text='Test update comment 1')
        mocked_comment = MagicMock()
        mocked_comment.scalar_one_or_none.return_value = Comment(id=1, user_id=1, image_id=1, text='Test comment 1',
                                                                 created_at=datetime(2024, 2, 24),
                                                                 updated_at=datetime(2024, 2, 24))
        self.session.execute.return_value = mocked_comment
        result = await update_comment(1, body, self.session, self.user)
        self.assertIsInstance(result, Comment)
        self.assertEqual(result.text, body.text)

    async def test_delete_comment(self):
        """
        The test_delete_comment function tests the delete_comment function in the comments.py file.
        It does this by creating a mocked comment object, and then using that to test whether or not
        the delete_comment function is able to successfully remove a comment from the database.

        :param self: Represent the instance of the object that is passed to the method when it is called
        :return: An instance of the comment class
        """
        mocked_comment = MagicMock()
        mocked_comment.scalar_one_or_none.return_value = Comment(id=1, user_id=1, image_id=1, text='Test comment 1',
                                                                 created_at=datetime(2024, 2, 24),
                                                                 updated_at=datetime(2024, 2, 24))
        self.session.execute.return_value = mocked_comment
        result = await delete_comment(1, self.session)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Comment)