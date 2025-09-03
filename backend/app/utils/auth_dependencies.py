from fastapi import HTTPException, Header
from typing import Optional, Dict, Any
from ..db.supabase_client import auth_request


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Validate Supabase access token by calling Supabase /auth/v1/user endpoint.
    Returns a normalized user dict with at least 'id' and 'email'. Raises HTTPException(401) on failure.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail='Missing Authorization header')

    token = authorization.split(' ', 1)[1] if authorization.startswith('Bearer ') else authorization

    res = await auth_request('GET', '/user', token=token)
    status = res.get('status_code') if isinstance(res, dict) else None

    if status != 200:
        raise HTTPException(status_code=401, detail='Invalid or expired token')

    data = res.get('data') or {}
    # Normalize role claim (supabase uses app_metadata or user_metadata; tests expect 'role')
    role = data.get('role') or (data.get('user_metadata') or {}).get('role') or (data.get('app_metadata') or {}).get('role') or 'citizen'
    normalized = {
        'id': data.get('id'),
        'email': data.get('email'),
        'role': role,
        'raw': data
    }
    return normalized

