from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Comment, User, Image
from src.schemas.comment import CommentSchema


async def create_comment(body: CommentSchema, image_id: int, db: AsyncSession, user: User):
    """
    Create a new comment in the database.

    :param body: The schema representing the comment data.
    :type body: CommentSchema
    :param image_id: The ID of the picture associated with the comment.
    :type image_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user creating the comment.
    :type user: User
    :return: The created comment.
    :rtype: Comment
    """
    comment = Comment(**body.model_dump(exclude_unset=True), user_id=user.id, image_id=image_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments(image_id: int, offset: int, limit: int, db: AsyncSession):
    """
    Retrieve a list of comments for a specific picture from the database.

    :param image_id: The ID of the picture for which comments are retrieved.
    :type image_id: int
    :param offset: The offset for pagination.
    :type offset: int
    :param limit: The limit for the number of comments to retrieve.
    :type limit: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: A list of comments.
    :rtype: List[Comment]
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
    Update a specific comment's text content in the database.

    :param comment_id: The ID of the comment to update.
    :type comment_id: int
    :param body: The schema representing the updated comment data.
    :type body: CommentSchema
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user updating the comment.
    :type user: User
    :return: The updated comment or None if not found.
    :rtype: Optional[Comment]
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
    Delete a specific comment from the database.

    :param comment_id: The ID of the comment to delete.
    :type comment_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :return: The deleted comment or None if not found.
    :rtype: Optional[Comment]
    """
    statement = select(Comment).filter_by(id=comment_id)
    comment = await db.execute(statement)
    comment = comment.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment