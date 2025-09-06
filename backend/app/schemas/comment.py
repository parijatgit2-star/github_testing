from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommentCreate(BaseModel):
    """Request schema for creating a new comment."""
    text: str


class CommentResponse(BaseModel):
    """Response schema for a single comment."""
    id: int
    issue_id: str
    user_id: str
    text: str
    created_at: Optional[datetime]

    class Config:
        """Pydantic configuration."""
        orm_mode = True
