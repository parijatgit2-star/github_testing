from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from ..schemas.auth import SignupRequest, LoginRequest
from ..schemas.api_models import AuthLoginResponse, SimpleOK
from ..services.auth_service import signup_user, login_user
from ..db.supabase_client import auth_request

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', status_code=201, response_model=SimpleOK)
async def signup(payload: SignupRequest):
    res = await signup_user(payload)
    if not res.get('ok'):
        raise HTTPException(status_code=400, detail=res.get('error', 'Signup failed'))
    return {'ok': True, 'data': res.get('data')}


@router.post('/login', response_model=AuthLoginResponse)
async def login(payload: LoginRequest):
    res = await login_user(payload)
    if not res.get('ok'):
        raise HTTPException(status_code=401, detail=res.get('error', 'Invalid credentials'))
    # Supabase returns access_token and refresh_token in data
    data = res.get('data') or {}
    return {'access_token': data.get('access_token'), 'token_type': 'bearer'}



@router.post('/logout', response_model=SimpleOK)
async def logout(authorization: Optional[str] = Header(None)):
    """Invalidate the current session token (Supabase sign out)."""
    if not authorization:
        raise HTTPException(status_code=401, detail='Missing Authorization')
    token = authorization.split(' ', 1)[1] if authorization.startswith('Bearer ') else authorization
    res = await auth_request('POST', '/logout', token=token)
    if res.get('status_code') not in (200, 204):
        raise HTTPException(status_code=400, detail='Failed to logout')
    return {'ok': True}


@router.post('/refresh', response_model=AuthLoginResponse)
async def refresh(token: str):
    """Exchange refresh token for a new access token (mock using auth_request)."""
    res = await auth_request('POST', '/token', payload={'grant_type': 'refresh_token', 'refresh_token': token}, form=True)
    if res.get('status_code') != 200:
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    data = res.get('data') or {}
    return {'access_token': data.get('access_token'), 'token_type': 'bearer'}


@router.post('/reset-password', response_model=SimpleOK)
async def reset_password(payload: dict):
    """Mock password reset: in production trigger email via Supabase/Auth or SMTP."""
    # We'll accept {email: str} and return ok for testing
    if not payload.get('email'):
        raise HTTPException(status_code=400, detail='email required')
    return {'ok': True}
