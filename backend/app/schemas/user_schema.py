from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    name: Optional[str]
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: Optional[str]
    email: EmailStr
    profile_image_url: Optional[str]

    class Config:
        orm_mode = True
