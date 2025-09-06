from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..db.supabase_client import supabase_request
from ..schemas.api_models import DeviceRegisterModel, DeviceResponseModel
from ..utils.auth_dependencies import get_current_user
from ..utils.validation import validate_single

router = APIRouter(prefix='/notifications', tags=['notifications'])


@router.get('/{user_id}', response_model=List[dict])
async def get_notifications(user_id: str):
    """Retrieves all notifications for a specific user.

    Args:
        user_id: The ID of the user whose notifications are to be fetched.

    Returns:
        A list of notification objects.
    """
    filters = {'user_id.eq': user_id}
    r = await supabase_request('GET', 'notifications', filters=filters)
    return r.get('data') or []


@router.post('/devices/register', response_model=DeviceResponseModel)
async def register_device(payload: DeviceRegisterModel, user=Depends(get_current_user)):
    """Registers a device token for receiving push notifications.

    This endpoint associates a device token (e.g., from FCM or APNS) with the
    authenticated user.

    Args:
        payload: A `DeviceRegisterModel` containing the device token and platform.
        user: The authenticated user, injected by FastAPI.

    Returns:
        The created device registration object.
    """
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    body = {'user_id': user.get('id'), 'device_token': payload.device_token, 'platform': payload.platform}
    r = await supabase_request('POST', 'devices', payload=body)
    data = r.get('data') or []
    return validate_single(DeviceResponseModel, data[0] if data else None)


@router.post('/push/send')
async def send_push(payload: dict, user=Depends(get_current_user)):
    """Sends a push notification.

    Note:
        This is a stub endpoint. In a production environment, this would
        integrate with a push notification service like Firebase Cloud
        Messaging (FCM) or Expo Push Notifications to actually deliver
        the notification. Currently, it only logs the push attempt.

    Args:
        payload: The content of the push notification.
        user: The authenticated user sending the notification.

    Returns:
        A dictionary indicating the success of the logging operation.
    """
    # In production integrate FCM/Expo here. We'll persist and return created row.
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    await supabase_request('POST', 'push_logs', payload={'entries': [{'sender_id': user.get('id'), 'payload': payload}]})
    return { 'ok': True }

