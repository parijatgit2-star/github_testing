from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ..db.supabase_client import supabase_request
from ..utils.auth_dependencies import get_current_user
from ..utils.validation import validate_single
from ..schemas.api_models import UserProfile

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserProfile)
async def get_me(user: Dict[str, Any] = Depends(get_current_user)):
	# get user profile from Supabase Auth /user already returned by dependency
	return validate_single(UserProfile, user)


@router.patch('/me', response_model=dict)
async def update_me(payload: Dict[str, Any], user: Dict[str, Any] = Depends(get_current_user)):
	# write to profiles table if present
	profile = {'id': user.get('id')}
	profile.update(payload)
	r = await supabase_request('PATCH', 'profiles', payload=profile, filters={'id.eq': user.get('id')})
	if r.get('status_code') not in (200, 204):
		raise HTTPException(status_code=400, detail='Failed to update profile')
	return {'ok': True}

