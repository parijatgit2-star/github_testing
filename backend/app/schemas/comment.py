from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommentCreate(BaseModel):
    text: str


class CommentResponse(BaseModel):
    id: int
    issue_id: str
    user_id: str
    text: str
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
