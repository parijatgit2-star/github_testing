from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# --- Auth models
class AuthRegister(BaseModel):
    """Schema for user registration data."""
    id: Optional[str]
    email: EmailStr


class AuthLoginResponse(BaseModel):
    """Response schema for a successful login, containing the access token."""
    access_token: str
    token_type: str = 'bearer'


class AuthRefreshResponse(BaseModel):
    """Response schema for a successful token refresh."""
    access_token: str
    token_type: str = 'bearer'


class SimpleOK(BaseModel):
    """Generic success response schema."""
    ok: bool = True


# --- User models
class UserProfile(BaseModel):
    """Schema for a user's public profile."""
    id: str
    email: EmailStr
    name: Optional[str]
    role: Optional[str]


# --- Issue models
class ImageItem(BaseModel):
    """Schema representing an uploaded image."""
    url: str
    public_id: Optional[str]


class IssueCreateModel(BaseModel):
    """Request schema for creating a new issue."""
    title: str
    description: str
    location: Optional[str]
    category: Optional[str]
    images: Optional[List[ImageItem]]


class IssueResponseModel(BaseModel):
    """Response schema for a single issue, including all its fields."""
    id: str
    title: str
    description: str
    location: Optional[str]
    category: Optional[str]
    status: str
    user_id: Optional[str]
    department_id: Optional[str]
    images: Optional[List[ImageItem]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class IssueListResponse(BaseModel):
    """Response schema for a list of issues."""
    issues: List[IssueResponseModel]


class IssueUpdateModel(BaseModel):
    """Request schema for updating an existing issue."""
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    department_id: Optional[str]


# --- Comment models
class CommentCreateModel(BaseModel):
    """Request schema for creating a new comment."""
    text: str


class CommentResponseModel(BaseModel):
    """Response schema for a single comment."""
    id: str
    issue_id: str
    user_id: str
    text: str
    created_at: Optional[datetime]


# --- Device models
class DeviceRegisterModel(BaseModel):
    """Request schema for registering a device for push notifications."""
    device_token: str
    platform: Optional[str]


class DeviceResponseModel(BaseModel):
    """Response schema for a registered device."""
    id: str
    user_id: str
    device_token: str
    platform: Optional[str]


# --- Analytics models
class IssuesByTimeItem(BaseModel):
    """Schema for a single data point in an issues-by-time analytics query."""
    date: str
    count: int


class ResponseTimesModel(BaseModel):
    """Response schema for the average issue response time analytic."""
    average_hours: Optional[float]
    count: int


class HotspotItem(BaseModel):
    """Schema for a single geographic hotspot in an analytics query."""
    lat: float
    lon: float
    count: int

