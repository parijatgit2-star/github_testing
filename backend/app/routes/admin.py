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
    """List users (admin only)."""
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    r = await supabase_request('GET', 'profiles')
    return r.get('data') or []


@router.patch('/users/{user_id}', response_model=SimpleOK)
async def update_user(user_id: str, payload: dict, user=Depends(get_current_user)):
    """Update a user (admin only)."""
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    await supabase_request('PATCH', 'profiles', payload=payload, filters={'id.eq': user_id})
    return {'ok': True}


@router.delete('/users/{user_id}', response_model=SimpleOK)
async def delete_user(user_id: str, user=Depends(get_current_user)):
    """Delete a user (admin only)."""
    if not user or user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail='Forbidden')
    await supabase_request('DELETE', 'profiles', filters={'id.eq': user_id})
    return {'ok': True}



@router.get('/analytics/issues-by-time', response_model=List[IssuesByTimeItem])
async def issues_by_time(days: int = 7, user=Depends(get_current_user)):
    """Return count of issues per day for the last `days` days."""
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
    """Return average response time (hours) for issues handled in the period."""
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
    """Return clusters of coordinates with high issue density (naive)."""
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
