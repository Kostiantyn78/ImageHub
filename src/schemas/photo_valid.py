from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ImageSchema(BaseModel):
    description: Optional[str] = Field(None, max_length=255, description="Photo description")
    tags: Optional[str] = Field(default=None, description="List of tags")

    class Config:
        json_schema_extra = {
            "example": {
                "description": "This is a photo of the city",
                "tags": ["City", "Landscape"]
            }
        }


class ImageUpdateSchema(BaseModel):
    description: Optional[str] = Field(None, max_length=255, description="Updated photo description")

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated photo description"
            }
        }


class ImageResponseSchema(BaseModel):
    user_id: int = Field(description="The ID of the user who uploaded the photo")
    picture_id: int = Field(description="Photo ID")
    url: str = Field(description="URL photo")
    description: Optional[str] = Field(None, description="Photo description")
    tags: List[str] = Field(default=[], description="List of tags")
    created_at: datetime = Field(description="Photo creation time")
    comments: Optional[List[str]] = Field(None, description="List of comments on the photo")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "picture_id": 1,
                "url": "http://example.com/photo.jpg",
                "description": "This is a photo of the city",
                "tags": ["ImageHubProjectDB", "ImageHubProjectDB"],
                "created_at": "2022-01-01T00:00:00",
                "comments": ["Beautiful photo!", "Thanks for the post!"]
            }
        }
