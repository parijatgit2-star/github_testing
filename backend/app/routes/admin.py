from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..db.supabase_client import supabase_request
from ..utils.auth_dependencies import get_current_user
from ..schemas.api_models import (
    SimpleOK,
    IssuesByTimeItem,
    ResponseTimesModel,
    HotspotItem,
)
from ..utils.validation import validate_list, validate_single

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get('/users', response_model=List[dict])
async def list_users(limit: int = 50, offset: int = 0, user=Depends(get_current_user)):
    """Lists all users in the system.

    This is a protected endpoint available only to admin users.

    Args:
        limit: The maximum number of users to return.
        offset: The starting offset for pagination.
        user: The authenticated user, injected by FastAPI.

    Returns:
        A list of user profile dictionaries.
    """
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    r = await supabase_request('GET', 'profiles')
    return r.get('data') or []


@router.patch('/users/{user_id}', response_model=SimpleOK)
async def update_user(user_id: str, payload: dict, user=Depends(get_current_user)):
    """Updates a user's profile.

    This is a protected endpoint available only to admin users.

    Args:
        user_id: The ID of the user to update.
        payload: A dictionary containing the profile fields to update.
        user: The authenticated user, injected by FastAPI.

    Returns:
        A dictionary indicating success.
    """
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    await supabase_request('PATCH', 'profiles', payload=payload, filters={'id.eq': user_id})
    return {'ok': True}


@router.delete('/users/{user_id}', response_model=SimpleOK)
async def delete_user(user_id: str, user=Depends(get_current_user)):
    """Deletes a user from the system.

    This is a protected endpoint available only to admin users.

    Args:
        user_id: The ID of the user to delete.
        user: The authenticated user, injected by FastAPI.

    Returns:
        A dictionary indicating success.
    """
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    await supabase_request('DELETE', 'profiles', filters={'id.eq': user_id})
    return {'ok': True}



@router.get('/analytics/issues-by-time', response_model=List[IssuesByTimeItem])
async def issues_by_time(days: int = 7, user=Depends(get_current_user)):
    """Gets the number of issues created per day for a recent period.

    This is a protected endpoint available only to admin users. It provides
    data suitable for time-series charts.

    Args:
        days: The number of past days to include in the analysis.
        user: The authenticated user, injected by FastAPI.

    Returns:
        A list of items, each containing a date and the count of issues
        created on that date.
    """
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    # simple implementation: fetch recent issues and group by created_at date
    r = await supabase_request('GET', 'issues')
    rows = r.get('data') or []
    # naive grouping
    from collections import defaultdict
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    counts = defaultdict(int)
    for it in rows:
        ca = it.get('created_at')
        if not ca:
            continue
        try:
            d = datetime.fromisoformat(ca)
        except Exception:
            continue
        if d < cutoff:
            continue
        counts[d.date().isoformat()] += 1
    return validate_list(IssuesByTimeItem, [{'date': k, 'count': v} for k, v in sorted(counts.items())])


@router.get('/analytics/response-times', response_model=ResponseTimesModel)
async def response_times(days: int = 30, user=Depends(get_current_user)):
    """Calculates the average issue response time over a recent period.

    This is a protected endpoint available only to admin users. "Response time"
    is defined as the duration between issue creation and resolution.

    Args:
        days: The number of past days to include in the analysis.
        user: The authenticated user, injected by FastAPI.

    Returns:
        An object containing the average response time in hours and the
        total number of issues included in the calculation.
    """
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    r = await supabase_request('GET', 'issues')
    rows = r.get('data') or []
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    total = 0.0
    count = 0
    for it in rows:
        created = it.get('created_at')
        resolved = it.get('resolved_at')
        if not created or not resolved:
            continue
        try:
            c = datetime.fromisoformat(created)
            rtime = datetime.fromisoformat(resolved)
        except Exception:
            continue
        if c < cutoff:
            continue
        total += (rtime - c).total_seconds() / 3600.0
        count += 1
    avg = (total / count) if count else None
    return validate_single(ResponseTimesModel, {'average_hours': avg, 'count': count})


@router.get('/analytics/hotspots', response_model=List[HotspotItem])
async def hotspots(radius_meters: int = 250, days: int = 30, user=Depends(get_current_user)):
    """Identifies geographic hotspots with a high density of reported issues.

    This is a protected endpoint available only to admin users. It uses a naive
    clustering algorithm based on rounding coordinates.

    Args:
        radius_meters: The radius to consider for clustering (currently unused
            as the implementation uses a simple rounding approach).
        days: The number of past days to include in the analysis.
        user: The authenticated user, injected by FastAPI.

    Returns:
        A list of hotspot items, each containing a latitude, longitude, and
        the count of issues in that cluster.
    """
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    r = await supabase_request('GET', 'issues')
    rows = r.get('data') or []
    # naive approach: group by rounded lat/lon
    from collections import defaultdict
    def round_coord(coord):
        try:
            return round(float(coord), 3)
        except Exception:
            return None
    groups = defaultdict(int)
    for it in rows:
        loc = it.get('location')
        if not loc:
            continue
        # expect 'lat,lon'
        parts = str(loc).split(',')
        if len(parts) < 2:
            continue
        lat = round_coord(parts[0])
        lon = round_coord(parts[1])
        if lat is None or lon is None:
            continue
        groups[(lat, lon)] += 1
    hotspots = []
    for (lat, lon), cnt in groups.items():
        hotspots.append({'lat': lat, 'lon': lon, 'count': cnt})
    hotspots.sort(key=lambda x: x['count'], reverse=True)
    return validate_list(HotspotItem, hotspots[:20])
