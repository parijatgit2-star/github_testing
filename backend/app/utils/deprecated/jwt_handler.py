"""
Archived JWT handler. Kept for reference only.
Do not import from here — use Supabase Auth via `utils.auth_dependencies.get_current_user`.
"""

def legacy_sign(payload: dict) -> str:
    """Legacy placeholder - returns a fake token for reference only."""
    return 'legacy.token.placeholder'
"""
Legacy JWT helpers moved to deprecated. Do not use — project uses Supabase Auth.
"""
raise SystemExit('jwt_handler removed: use Supabase Auth')
