from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import comments as repository_comments
from src.schemas.comment import CommentSchema, CommentResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/comments', tags=["Comments"])
delete_access = RoleAccess([Role.admin, Role.moderator])


@router.post('/{image_id}', response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
        body: CommentSchema,
        image_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """
    Endpoint to create a new comment on an image.

    :param body: CommentSchema instance containing comment data.
    :type body: CommentSchema
    :param image_id: ID of the image to which the comment is associated.
    :type image_id: int
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :param user: Current authenticated user (dependency injection).
    :type user: User
    :return: The created comment.
    :rtype: CommentResponse
    :raises HTTPException: If the text is missing or the request is malformed.
    """
    if not body.text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The text is missing')
    try:
        comment = await repository_comments.create_comment(body, image_id, db, user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The request is malformed')
    return comment


@router.get('/all/{image_id}', response_model=list[CommentResponse])
async def get_comments(
        image_id: int = Path(ge=1),
        offset: int = Query(0, ge=0),
        limit: int = Query(10, ge=10, le=100),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to retrieve a list of comments for a specific image.

    :param image_id: ID of the image for which comments are to be retrieved.
    :type image_id: int
    :param offset: Offset for pagination.
    :type offset: int
    :param limit: Limit for pagination.
    :type limit: int
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: List of comments.
    :rtype: list[CommentResponse]
    :raises HTTPException: If the image is not found.
    """
    comments = await repository_comments.get_comments(image_id, offset, limit, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The image is not found")
    return comments


@router.patch('/{comment_id}', response_model=CommentResponse)
async def update_comment(
        body: CommentSchema,
        comment_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """
    Endpoint to update the text of a specific comment by its ID.

    :param body: CommentSchema instance containing updated comment data.
    :type body: CommentSchema
    :param comment_id: ID of the comment to be updated.
    :type comment_id: int
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :param user: Current authenticated user (dependency injection).
    :type user: User
    :return: The updated comment.
    :rtype: CommentResponse
    :raises HTTPException: If the text is missing, the request is malformed, or the comment is not found.
    """
    if not body.text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The text is missing')
    try:
        comment = await repository_comments.update_comment(comment_id, body, db, user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The request is malformed')
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='The comment is not found')
    return comment


@router.delete('/{comment_id}', response_model=CommentResponse, dependencies=[Depends(delete_access)])
async def delete_comment(
        comment_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to delete a specific comment by its ID.

    :param comment_id: ID of the comment to be deleted.
    :type comment_id: int
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The deleted comment.
    :rtype: CommentResponse
    :raises HTTPException: If the comment is not found or the user lacks the necessary permissions.
    """
    comment = await repository_comments.delete_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="the comment is not found or the user lacks"
                                                                          " the necessary permissions")
    return comment