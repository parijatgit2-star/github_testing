from pydantic import BaseModel


class FAQ(BaseModel):
    question: str
    answer: str


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
