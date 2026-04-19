from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50, example="john_doe")
    email: EmailStr = Field(max_length=120, example="john_doe@example.com")


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100, example="My First Post")
    content: str = Field(min_length=1, example="This is the content of my first post.")


class PostCreate(PostBase):
    user_id: int  # TEMPORARY


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse

