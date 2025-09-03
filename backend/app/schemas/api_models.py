from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# --- Auth models
class AuthRegister(BaseModel):
    id: Optional[str]
    email: EmailStr


class AuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class AuthRefreshResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class SimpleOK(BaseModel):
    ok: bool = True


# --- User models
class UserProfile(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str]
    role: Optional[str]


# --- Issue models
class ImageItem(BaseModel):
    url: str
    public_id: Optional[str]


class IssueCreateModel(BaseModel):
    title: str
    description: str
    location: Optional[str]
    category: Optional[str]
    images: Optional[List[ImageItem]]


class IssueResponseModel(BaseModel):
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
    issues: List[IssueResponseModel]


class IssueUpdateModel(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    department_id: Optional[str]


# --- Comment models
class CommentCreateModel(BaseModel):
    text: str


class CommentResponseModel(BaseModel):
    id: str
    issue_id: str
    user_id: str
    text: str
    created_at: Optional[datetime]


# --- Device models
class DeviceRegisterModel(BaseModel):
    device_token: str
    platform: Optional[str]


class DeviceResponseModel(BaseModel):
    id: str
    user_id: str
    device_token: str
    platform: Optional[str]


# --- Analytics models
class IssuesByTimeItem(BaseModel):
    date: str
    count: int


class ResponseTimesModel(BaseModel):
    average_hours: Optional[float]
    count: int


class HotspotItem(BaseModel):
    lat: float
    lon: float
    count: int

