from ..db.supabase_client import auth_request
from ..schemas.auth import SignupRequest, LoginRequest
from typing import Dict, Any


async def signup_user(data: SignupRequest) -> Dict[str, Any]:
    """Signs up a new user using Supabase Auth.

    Args:
        data: An object containing the user's email and password.

    Returns:
        A dictionary indicating success or failure. On success, it includes
        the user data from Supabase. On failure, it includes an error message.
    """
    # Use Supabase Auth signup endpoint
    payload = {"email": data.email, "password": data.password}
    res = await auth_request('POST', '/signup', payload=payload)
    if res.get('status_code') not in (200, 201):
        return {'ok': False, 'error': res.get('data') or res.get('error')}
    return {'ok': True, 'data': res.get('data')}


async def login_user(data: LoginRequest) -> Dict[str, Any]:
    """Logs in a user using Supabase Auth.

    This function authenticates a user by sending their credentials to the
    Supabase token endpoint, exchanging them for an access token.

    Args:
        data: An object containing the user's email and password.

    Returns:
        A dictionary indicating success or failure. On success, it includes
        the access token and user data. On failure, it includes an error
        message.
    """
    # Use Supabase token endpoint: form data grant_type=password
    payload = {'grant_type': 'password', 'username': data.email, 'password': data.password}
    res = await auth_request('POST', '/token', payload=payload, form=True)
    if res.get('status_code') != 200:
        return {'ok': False, 'error': res.get('data') or res.get('error')}
    return {'ok': True, 'data': res.get('data')}
