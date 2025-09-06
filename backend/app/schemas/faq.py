from pydantic import BaseModel


class FAQ(BaseModel):
    """Schema representing a single Frequently Asked Question."""
    question: str
    answer: str


class AskRequest(BaseModel):
    """Request schema for asking a question to the FAQ model."""
    question: str


class AskResponse(BaseModel):
    """Response schema containing the answer from the FAQ model."""
    answer: str
