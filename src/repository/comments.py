from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Comment, User, Image
from src.schemas.comment import CommentSchema


async def create_comment(body: CommentSchema, image_id: int, db: AsyncSession, user: User):
    """
    The create_comment function creates a new comment in the database.

    :param body: CommentSchema: Validate the comment body
    :param image_id: int: Specify the image that the comment is being added to
    :param db: AsyncSession: Pass in the database session
    :param user: User: Get the user_id of the comment
    :return: A comment object
    """
    comment = Comment(**body.model_dump(exclude_unset=True), user_id=user.id, image_id=image_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments(image_id: int, offset: int, limit: int, db: AsyncSession):
    """
    The get_comments function takes in an image_id, offset, and limit.
    It then queries the database for the image with that id. If it exists,
    it returns a list of comments associated with that image.

    :param image_id: int: Specify the image id of the comments you want to retrieve
    :param offset: int: Set the offset of the comments to be returned
    :param limit: int: Limit the number of comments returned
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of comments
    """
    statement = select(Image).where(Image.id == image_id)
    image = await db.execute(statement)
    image = image.unique().scalar_one_or_none()
    if image:
        statement = select(Comment).filter_by(image_id=image_id).offset(offset).limit(limit)
        comments = await db.execute(statement)
        return comments.scalars().all()


async def update_comment(comment_id: int, body: CommentSchema, db: AsyncSession, user: User):
    """
    The update_comment function updates a comment in the database.

    :param comment_id: int: Select the comment to be updated
    :param body: CommentSchema: Pass the new comment text to the function
    :param db: AsyncSession: Connect to the database
    :param user: User: Ensure that the user is authorized to update the comment
    :return: A comment object
    """
    statement = select(Comment).filter_by(id=comment_id, user_id=user.id)
    comment = await db.execute(statement)
    comment = comment.scalar_one_or_none()
    if comment:
        comment.text = body.text
        await db.commit()
        await db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, db: AsyncSession):
    """
    The delete_comment function deletes a comment from the database.
        Args:
            comment_id (int): The id of the comment to be deleted.
            db (AsyncSession): An async session object for interacting with the database.

    :param comment_id: int: Specify the comment to be deleted
    :param db: AsyncSession: Pass in the database session
    :return: A comment object
    """
    statement = select(Comment).filter_by(id=comment_id)
    comment = await db.execute(statement)
    comment = comment.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment