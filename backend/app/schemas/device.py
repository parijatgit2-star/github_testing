from pydantic import BaseModel
from typing import Optional


class DeviceRegister(BaseModel):
    user_id: str
    device_token: str
    platform: Optional[str] = 'unknown'


class DeviceResponse(BaseModel):
    id: int
    user_id: str
    device_token: str
    platform: Optional[str]

    class Config:
        orm_mode = True
