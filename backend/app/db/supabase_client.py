from typing import Any, Dict, Optional
import httpx
from ..config import settings


BASE_REST = str(settings.SUPABASE_URL).rstrip('/') + '/rest/v1'
BASE_AUTH = str(settings.SUPABASE_URL).rstrip('/') + '/auth/v1'
API_KEY = settings.SUPABASE_KEY


def _build_filters(filters: Optional[Dict[str, Any]]) -> Optional[str]:
    if not filters:
        return None
    parts = []
    for k, v in filters.items():
        if '.' in k:
            col, op = k.split('.', 1)
            parts.append(f"{col}={op}.{v}")
        else:
            parts.append(f"{k}=eq.{v}")
    return '&'.join(parts)


async def supabase_request(method: str, table: str, payload: Optional[Dict] = None, filters: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None):
    url = f"{BASE_REST}/{table}"
    params = _build_filters(filters)
    req_headers = {
        'apikey': API_KEY,
        'Authorization': f'Bearer {API_KEY}',
        'Accept': 'application/json',
    }
    if headers:
        req_headers.update(headers)

    async with httpx.AsyncClient() as client:
        if method.upper() == 'GET':
            full_url = url + (f"?{params}" if params else '')
            r = await client.get(full_url, headers=req_headers)
        elif method.upper() == 'POST':
            r = await client.post(url, json=payload, headers=req_headers)
        elif method.upper() == 'PATCH':
            full_url = url + (f"?{params}" if params else '')
            r = await client.patch(full_url, json=payload, headers=req_headers)
        elif method.upper() == 'DELETE':
            full_url = url + (f"?{params}" if params else '')
            r = await client.delete(full_url, headers=req_headers)
        else:
            raise ValueError('Unsupported method')

        try:
            data = r.json()
        except Exception:
            data = {'text': r.text}
        return {'status_code': r.status_code, 'data': data, 'headers': dict(r.headers)}


async def auth_request(method: str, path: str, payload: Optional[Dict] = None, token: Optional[str] = None, form: bool = False):
    """Call Supabase Auth endpoints under /auth/v1{path}.
    path should start with '/'. If form=True payload will be sent as form data.
    """
    url = BASE_AUTH + path
    req_headers = {'apikey': API_KEY, 'Accept': 'application/json'}
    if token:
        req_headers['Authorization'] = f'Bearer {token}'

    async with httpx.AsyncClient() as client:
        if method.upper() == 'GET':
            r = await client.get(url, headers=req_headers)
        elif method.upper() == 'POST':
            if form:
                r = await client.post(url, data=payload, headers={'apikey': API_KEY, 'Accept': 'application/json'})
            else:
                r = await client.post(url, json=payload, headers=req_headers)
        elif method.upper() == 'DELETE':
            r = await client.delete(url, headers=req_headers)
        else:
            raise ValueError('Unsupported auth method')
        try:
            data = r.json()
        except Exception:
            data = {'text': r.text}
        return {'status_code': r.status_code, 'data': data, 'headers': dict(r.headers)}


