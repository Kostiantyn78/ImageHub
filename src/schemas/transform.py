from datetime import datetime
from typing import Optional, Dict, Union

from pydantic import BaseModel, Field


class TransformModel(BaseModel):
    """
    A Pydantic model designed to validate incoming parameters for a transformation.

    Possible (but not all) image transformation options:
    "height": "The height of the transformed image. 100-2000",
    "width": "The width of the transformed image. 100-2000",
    "effects": ["saturation", "sharpen", "grayscale", "sepia", "vignette", "pixelate", "blur"],
    "crop": ["fill", "fit", "limit", "thumb", "scale"],
    "border": ["10px_solid_red", "5px_solid_lightblue", "15px_solid_lightyellow"]
    """

    params_of_transform: Dict[str, Union[str, int]] = Field(
        default_factory=dict,
        example={'height': 250, 'width': 250,
                 'effect': "vignette",
                 'crop': "scale",
                 'border': "30px_solid_lightyellow",
                 'angle': 18
                 }
    )


class TransformResponse(BaseModel):
    """A Pydantic model crafted for serializing transformation data in responses."""
    id: int
    natural_photo_id: int
    image_url: str
    qr_code_url: Optional[str]
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
