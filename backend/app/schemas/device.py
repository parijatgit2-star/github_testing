from pydantic import BaseModel
from typing import Optional


class DeviceRegister(BaseModel):
    """Schema for registering a new device for push notifications."""
    user_id: str
    device_token: str
    platform: Optional[str] = 'unknown'


class DeviceResponse(BaseModel):
    """Response schema for a registered device."""
    id: int
    user_id: str
    device_token: str
    platform: Optional[str]

    class Config:
        """Pydantic configuration."""
        orm_mode = True
