from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository.transform import TransformRepository
from src.schemas.transform import TransformModel, TransformResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/transform', tags=['Transforming'])


def verify_permissions(image, current_user: User):
    """
    The verify_permissions function is used to verify that the user has permission to perform an action on a given image.
        It takes in two parameters:
            - image: The Image object being acted upon.
            - current_user: The User object of the currently logged-in user.

    :param image: Pass the image object to the function
    :param current_user: User: Pass the current user to the function
    :return: The image object if the user has rights to perform the action
    """
    if not image:
        raise HTTPException(status_code=404, detail="Image Not Found")
    if image.user_id != current_user.id and current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="You do not have rights to perform this action")
    return


@router.post('/create_transform/{natural_photo_id}', response_model=TransformResponse,
             status_code=status.HTTP_201_CREATED)
async def create_transform(request: TransformModel, natural_photo_id: int = Path(ge=1),
                           current_user: User = Depends(auth_service.get_current_user),
                           session: AsyncSession = Depends(get_db)):
    """
    Possible (but not all) image transformation options:

    "height": "The height of the transformed image. 100-2000",

    "width": "The width of the transformed image. 100-2000",

    "effects": ["saturation", "sharpen", "grayscale", "sepia", "vignette", "pixelate", "blur"],

    "crop": ["fill", "fit", "limit", "thumb", "scale"],

    "border": ["10px_solid_red", "5px_solid_lightblue", "15px_solid_lightyellow"]
    """
    transform_repository = TransformRepository(session)
    params_of_transform = request.params_of_transform
    image = await transform_repository.get_image_by_id(natural_photo_id)
    verify_permissions(image, current_user)
    if not params_of_transform:
        raise HTTPException(status_code=400, detail="At least one transformation parameter must be specified")
    transformed_image = await transform_repository.create_transformed_image(
        user_id=image.user_id,
        natural_photo_id=natural_photo_id,
        params_of_transform=params_of_transform
    )
    if transformed_image is None:
        raise HTTPException(status_code=500, detail='Internal Server Error. The transformation is not done')
    return transformed_image


@router.get("/user_transforms", response_model=List[TransformResponse], status_code=status.HTTP_200_OK)
async def all_user_transforms(current_user: User = Depends(auth_service.get_current_user),
                              session: AsyncSession = Depends(get_db)):
    """
    The all_user_transforms function returns all the transforms for a given user.
        The function takes in an optional current_user parameter, which is used to identify the user.
        If no current_user is provided, then it will return an error message.

    :param current_user: User: Get the current user
    :param session: AsyncSession: Create a database session
    :return: A list of all transforms associated with the current user
    """
    transform_repository = TransformRepository(session)
    user_transforms = await transform_repository.get_transforms_by_user_id(current_user.id)
    if user_transforms is None:
        raise HTTPException(status_code=404, detail="Image Not Found")
    return user_transforms


@router.get("/{transform_id}", response_model=TransformResponse, status_code=status.HTTP_200_OK)
async def get_transform(transform_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                        session: AsyncSession = Depends(get_db)):
    """
    The get_transform function returns a transformed image based on the transform_id.
        The function requires an authenticated user and a database session.

    :param transform_id: int: Get the transform from the database
    :param current_user: User: Verify that the user has permission to view the image
    :param session: AsyncSession: Pass the database connection to the repository
    :return: A transformed image
    """
    transform_repository = TransformRepository(session)
    transformed_image = await transform_repository.get_transformed_image(transform_id)
    verify_permissions(transformed_image, current_user)
    return transformed_image


@router.get("/{transform_id}/qr_code", status_code=status.HTTP_200_OK)
async def get_transform_qr_code(transform_id: int = Path(ge=1),
                                current_user: User = Depends(auth_service.get_current_user),
                                session: AsyncSession = Depends(get_db)):
    """
    The get_transform_qr_code function returns the QR code URL for a given transform ID.

    :param transform_id: int: Get the transform id from the path
    :param current_user: User: Get the user that is currently logged in
    :param session: AsyncSession: Access the database
    :return: The qr_code_url of the transformed image
    """
    transform_repository = TransformRepository(session)
    transformed_image = await transform_repository.get_transformed_image(transform_id)
    verify_permissions(transformed_image, current_user)
    return {"qr_code_url": transformed_image.qr_code_url}


@router.patch("/{transform_id}", response_model=TransformResponse, status_code=status.HTTP_200_OK)
async def update_transform(request: TransformModel, transform_id: int = Path(ge=1),
                           current_user: User = Depends(auth_service.get_current_user),
                           session: AsyncSession = Depends(get_db)):
    """
    The update_transform function updates the transformation of an image.
        The function takes in a TransformModel object, which contains the parameters for the transformation.
        It also takes in a transform_id, which is used to identify what transformed image we are updating.
        The current_user and session objects are passed into this function by dependency injection.

    :param request: TransformModel: Get the parameters of the transformation
    :param transform_id: int: Get the transformed image from the database
    :param current_user: User: Get the current user from the token
    :param session: AsyncSession: Get the database session
    :return: The transformed image with the new parameters
    """
    transform_repository = TransformRepository(session)
    transformed_image = await transform_repository.get_transformed_image(transform_id)
    verify_permissions(transformed_image, current_user)
    new_transformed_image = await transform_repository.update_transformed_image(
        transformed_image_id=transform_id,
        params_of_transform=request.params_of_transform)
    if not new_transformed_image:
        raise HTTPException(status_code=500, detail='Internal Server Error. The transformation is not done')
    return new_transformed_image


@router.delete("/{transform_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transform(transform_id: int, current_user: User = Depends(auth_service.get_current_user),
                           session: AsyncSession = Depends(get_db)):
    """
    The delete_transform function is used to delete a transformed image from the database.
        The function takes in an integer representing the id of the transform and returns a boolean value indicating whether or not
        it was successful. If it was unsuccessful, then an HTTPException is raised with status code 404.

    :param transform_id: int: Identify the transform that is to be deleted
    :param current_user: User: Get the current user from the auth_service
    :param session: AsyncSession: Create a database session
    :return: A boolean value
    """
    transform_repository = TransformRepository(session)
    transformed_image = await transform_repository.get_transformed_image(transform_id)
    verify_permissions(transformed_image, current_user)
    deleted = await transform_repository.delete_transformed_image(transform_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Unfortunately the deletion was not completed")
