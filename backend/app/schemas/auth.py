from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    """Request schema for user signup."""
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Response schema for a successful login, containing the access token."""
    access_token: str
    token_type: str = 'bearer'
