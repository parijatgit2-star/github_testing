from pydantic import BaseModel
from typing import Optional


class IssueCreate(BaseModel):
    description: str
    location: Optional[str]


class IssueResponse(BaseModel):
    id: int
    description: str
    location: Optional[str]
    image_url: Optional[str]
    status: str

    class Config:
        orm_mode = True
