"""Utilities package for backend app."""

__all__ = [
    'auth_dependencies',
    'error_handler',
    'require_role',
    'get_current_user',
]

from .auth_dependencies import get_current_user

def require_role(role: str):
    """Return a dependency that enforces the provided role."""
    async def _dep(user = None):
        if not user:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail='Unauthorized')
        if user.get('role') != role:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail='Forbidden')
        return user
    return _dep
 
