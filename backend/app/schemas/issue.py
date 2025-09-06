from pydantic import BaseModel
from typing import Optional


class IssueCreate(BaseModel):
    """Request schema for creating a new issue."""
    title: str
    description: str
    status: Optional[str] = 'pending'
    image: Optional[str] = None


class IssueUpdate(BaseModel):
    """Request schema for updating an existing issue."""
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
