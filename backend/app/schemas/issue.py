from pydantic import BaseModel
from typing import Optional


class IssueCreate(BaseModel):
    title: str
    description: str
    status: Optional[str] = 'pending'
    image: Optional[str] = None


class IssueUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
