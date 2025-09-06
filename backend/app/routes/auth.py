from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from ..schemas.auth import SignupRequest, LoginRequest
from ..schemas.api_models import AuthLoginResponse, SimpleOK
from ..services.auth_service import signup_user, login_user
from ..db.supabase_client import auth_request

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', status_code=201, response_model=SimpleOK)
async def signup(payload: SignupRequest):
    """Handles user registration.

    Args:
        payload: A `SignupRequest` object containing the user's email and password.

    Returns:
        A dictionary indicating the success of the operation.

    Raises:
        HTTPException: If the signup process fails (e.g., user already exists).
    """
    res = await signup_user(payload)
    if not res.get('ok'):
        raise HTTPException(status_code=400, detail=res.get('error', 'Signup failed'))
    return {'ok': True, 'data': res.get('data')}


@router.post('/login', response_model=AuthLoginResponse)
async def login(payload: LoginRequest):
    """Handles user login and returns an access token.

    Args:
        payload: A `LoginRequest` object containing the user's email and password.

    Returns:
        An `AuthLoginResponse` containing the access token and token type.

    Raises:
        HTTPException: If the login credentials are invalid.
    """
    res = await login_user(payload)
    if not res.get('ok'):
        raise HTTPException(status_code=401, detail=res.get('error', 'Invalid credentials'))
    # Supabase returns access_token and refresh_token in data
    data = res.get('data') or {}
    return {'access_token': data.get('access_token'), 'token_type': 'bearer'}



@router.post('/logout', response_model=SimpleOK)
async def logout(authorization: Optional[str] = Header(None)):
    """Invalidates the user's current session token via Supabase sign out.

    Args:
        authorization: The 'Authorization' header containing the Bearer token.

    Returns:
        A dictionary indicating the success of the operation.

    Raises:
        HTTPException: If the logout process fails or the token is missing.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail='Missing Authorization')
    token = authorization.split(' ', 1)[1] if authorization.startswith('Bearer ') else authorization
    res = await auth_request('POST', '/logout', token=token)
    if res.get('status_code') not in (200, 204):
        raise HTTPException(status_code=400, detail='Failed to logout')
    return {'ok': True}


@router.post('/refresh', response_model=AuthLoginResponse)
async def refresh(token: str):
    """Exchanges a refresh token for a new access token.

    Args:
        token: The refresh token provided by Supabase upon login.

    Returns:
        An `AuthLoginResponse` containing the new access token and token type.

    Raises:
        HTTPException: If the refresh token is invalid.
    """
    res = await auth_request('POST', '/token', payload={'grant_type': 'refresh_token', 'refresh_token': token}, form=True)
    if res.get('status_code') != 200:
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    data = res.get('data') or {}
    return {'access_token': data.get('access_token'), 'token_type': 'bearer'}


@router.post('/reset-password', response_model=SimpleOK)
async def reset_password(payload: dict):
    """Initiates the password reset process for a user.

    Note:
        This is a mock endpoint for testing purposes. In a production
        environment, this should trigger an email to the user via Supabase
        Auth or a dedicated SMTP service.

    Args:
        payload: A dictionary containing the user's email.

    Returns:
        A dictionary indicating the success of the request.
    """
    # We'll accept {email: str} and return ok for testing
    if not payload.get('email'):
        raise HTTPException(status_code=400, detail='email required')
    return {'ok': True}
