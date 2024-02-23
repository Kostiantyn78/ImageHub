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
    transform_repository = TransformRepository(session)
    user_transforms = await transform_repository.get_transforms_by_user_id(current_user.id)
    if user_transforms is None:
        raise HTTPException(status_code=404, detail="Image Not Found")
    return user_transforms


@router.get("/{transform_id}", response_model=TransformResponse, status_code=status.HTTP_200_OK)
async def get_transform(transform_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user),
                        session: AsyncSession = Depends(get_db)):
    transform_repository = TransformRepository(session)
    transformed_image = await transform_repository.get_transformed_image(transform_id)
    verify_permissions(transformed_image, current_user)
    return transformed_image


@router.get("/{transform_id}/qr_code", status_code=status.HTTP_200_OK)
async def get_transform_qr_code(transform_id: int = Path(ge=1),
                                current_user: User = Depends(auth_service.get_current_user),
                                session: AsyncSession = Depends(get_db)):
    transform_repository = TransformRepository(session)
    transformed_image = await transform_repository.get_transformed_image(transform_id)
    verify_permissions(transformed_image, current_user)
    return {"qr_code_url": transformed_image.qr_code_url}


@router.patch("/{transform_id}", response_model=TransformResponse, status_code=status.HTTP_200_OK)
async def update_transform(request: TransformModel, transform_id: int = Path(ge=1),
                           current_user: User = Depends(auth_service.get_current_user),
                           session: AsyncSession = Depends(get_db)):
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
    transform_repository = TransformRepository(session)
    transformed_image = await transform_repository.get_transformed_image(transform_id)
    verify_permissions(transformed_image, current_user)
    deleted = await transform_repository.delete_transformed_image(transform_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Unfortunately the deletion was not completed")
