from pydantic import BaseModel
from typing import Optional


class IssueCreate(BaseModel):
    """Schema for creating a new issue (alternative version)."""
    description: str
    location: Optional[str]


class IssueResponse(BaseModel):
    """Schema for an issue response (alternative version)."""
    id: int
    description: str
    location: Optional[str]
    image_url: Optional[str]
    status: str

    class Config:
        """Pydantic configuration."""
        orm_mode = True
