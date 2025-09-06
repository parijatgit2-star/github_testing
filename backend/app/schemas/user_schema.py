from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    """Schema for creating a new user (alternative version)."""
    name: Optional[str]
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Schema for user login (alternative version)."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response schema for a user profile (alternative version)."""
    id: int
    name: Optional[str]
    email: EmailStr
    profile_image_url: Optional[str]

    class Config:
        """Pydantic configuration."""
        orm_mode = True
