from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..db.supabase_client import supabase_request
from ..schemas.api_models import DeviceRegisterModel, DeviceResponseModel
from ..utils.auth_dependencies import get_current_user
from ..utils.validation import validate_single

router = APIRouter(prefix='/notifications', tags=['notifications'])


@router.get('/{user_id}', response_model=List[dict])
async def get_notifications(user_id: str):
    """Get notifications for a user."""
    filters = {'user_id.eq': user_id}
    r = await supabase_request('GET', 'notifications', filters=filters)
    return r.get('data') or []


@router.post('/devices/register', response_model=DeviceResponseModel)
async def register_device(payload: DeviceRegisterModel, user=Depends(get_current_user)):
    """Register a device token for push notifications."""
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    body = {'user_id': user.get('id'), 'device_token': payload.device_token, 'platform': payload.platform}
    r = await supabase_request('POST', 'devices', payload=body)
    data = r.get('data') or []
    return validate_single(DeviceResponseModel, data[0] if data else None)


@router.post('/push/send')
async def send_push(payload: dict, user=Depends(get_current_user)):
    """Send a push notification to devices (stub)."""
    # In production integrate FCM/Expo here. We'll persist and return created row.
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    await supabase_request('POST', 'push_logs', payload={'entries': [{'sender_id': user.get('id'), 'payload': payload}]})
    return { 'ok': True }

