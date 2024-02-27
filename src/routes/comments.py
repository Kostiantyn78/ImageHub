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
    The create_comment function creates a new comment on an image.

    :param body: CommentSchema: Validate the request body
    :param image_id: int: Specify the id of the image to which
    :param db: AsyncSession: Inject the database session into the function
    :param user: User: Get the current authenticated user
    :param : Specify the id of the comment to be deleted
    :return: A commentresponse object
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
    The get_comments function returns a list of comments for the image with the given id.

    :param image_id: int: Get the comments of a specific image
    :param offset: int: Get the next set of comments
    :param ge: Specify the minimum value of a parameter
    :param limit: int: Limit the number of comments returned
    :param ge: Specify the minimum value of the parameter
    :param le: Limit the number of comments returned
    :param db: AsyncSession: Get the database session
    :param : Get the image id
    :return: A list of comments for the image with id = image_id
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
    The update_comment function updates a comment in the database.
        The function takes an id of the comment to be updated, and a body containing the new text for that comment.
        It returns an updated Comment object.

    :param body: CommentSchema: Validate the request body
    :param comment_id: int: Get the comment id from the path
    :param db: AsyncSession: Get the database session
    :param user: User: Check if the user is authenticated
    :param : Get the id of the comment to be deleted
    :return: The updated comment
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
    The delete_comment function deletes a comment from the database.
        The function takes in an integer representing the id of the comment to be deleted, and returns a dictionary containing
        information about that comment.

    :param comment_id: int: Identify the comment to be deleted
    :param db: AsyncSession: Get the database session
    :param : Get the comment id
    :return: The deleted comment
    """
    comment = await repository_comments.delete_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="the comment is not found or the user lacks"
                                                                          " the necessary permissions")
    return comment