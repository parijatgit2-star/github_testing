from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Notification(BaseModel):
    id: int
    user_id: str
    message: str
    created_at: Optional[datetime]
