
from typing import Optional, Dict, Any, List, Union
from ..db.supabase_client import supabase_request
from ..services.cloudinary_service import upload_image, delete_image
from ..schemas.issue import IssueCreate, IssueUpdate
from ..schemas.api_models import IssueCreateModel, IssueUpdateModel
from ..ai.model import detect_unwanted_submission
from .routing_engine import detect_department_from_text, map_department_name_to_id
import tempfile
import shutil
import os


async def create_issue(data: Union[IssueCreateModel, IssueCreate, Dict[str, Any]], image_files: Optional[List[Any]] = None, user: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Create an issue. Accepts a list of UploadFile-like objects in image_files.
    Runs spam detection before upload. Returns result dict.
    """
    # spam detection on text fields
    # Support Pydantic models, objects with attributes, or plain dict payloads
    if isinstance(data, dict):
        title = data.get('title')
        description = data.get('description')
    else:
        title = getattr(data, 'title', None)
        description = getattr(data, 'description', None)
    text = (title or '') + ' ' + (description or '')
    if detect_unwanted_submission(text):
        return {'ok': False, 'error': 'Submission flagged as spam'}

    uploaded: List[Dict[str, Any]] = []
    try:
        if image_files:
            for img in image_files:
                if not img:
                    continue
                # img is UploadFile - write to temp file
                tmp = tempfile.NamedTemporaryFile(delete=False)
                try:
                    shutil.copyfileobj(img.file, tmp)
                    tmp.flush()
                    # await the async upload
                    res = await upload_image(tmp.name)
                    if res:
                        uploaded.append({'url': res.get('secure_url'), 'public_id': res.get('public_id')})
                finally:
                    tmp.close()
                    try:
                        os.unlink(tmp.name)
                    except Exception:
                        pass

        # attempt to auto-detect department from title/description
        combined_text = f"{title or ''} {description or ''}"
        dept_name = detect_department_from_text(combined_text)
        department_id = None
        if dept_name:
            # fetch departments once and map name->id
            dres = await supabase_request('GET', 'departments')
            rows = dres.get('data') or []
            # build mapping id->name
            id_to_name = {r.get('id'): r.get('name') for r in rows}
            department_id = map_department_name_to_id(id_to_name, dept_name)

        payload = {
            'title': title,
            'description': description,
            'status': getattr(data, 'status', None) or 'pending',
            'images': uploaded,
            'user_id': user.get('id') if user else None,
            'department_id': department_id
        }

        # pass a single payload mapping
        r = await supabase_request('POST', 'issues', payload=payload)
        if r.get('status_code') in (200, 201):
            created = r.get('data')
            # Supabase may return list
            if isinstance(created, list) and created:
                return created[0]
            return created
        # on failure raise to be handled by caller
        raise Exception(r.get('data'))
    except Exception as exc:
        # attempt to cleanup uploaded images on failure
        for u in uploaded:
            if u.get('public_id'):
                try:
                    await delete_image(u.get('public_id'))
                except Exception:
                    pass
        # Re-raise the original exception so callers (routes) can convert to HTTP errors
        raise


async def get_issues() -> Any:
    r = await supabase_request('GET', 'issues')
    return r.get('data')


async def get_issue(id: str) -> Optional[Dict[str, Any]]:
    filters = {'id.eq': id}
    r = await supabase_request('GET', 'issues', filters=filters)
    rows = r.get('data') or []
    return rows[0] if rows else None


async def update_issue(id: str, data: Union[IssueUpdateModel, IssueUpdate, Dict[str, Any]], user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    # fetch existing to detect status changes
    existing = await get_issue(id)
    # accept Pydantic model or dict-like
    if hasattr(data, 'dict'):
        payload = {k: v for k, v in data.dict().items() if v is not None}
    elif isinstance(data, dict):
        payload = {k: v for k, v in data.items() if v is not None}
    else:
        # fallback for objects with attributes
        payload = {k: getattr(data, k) for k in ('title', 'description', 'status', 'department_id') if getattr(data, k, None) is not None}
    filters = {'id.eq': id}
    r = await supabase_request('PATCH', 'issues', payload=payload, filters=filters)
    if r.get('status_code') in (200, 204):
        # notify user if status changed
        try:
            new_status = payload.get('status')
            old_status = existing.get('status') if existing else None
            if new_status and old_status and new_status != old_status:
                note = {
                    'user_id': existing.get('user_id'),
                    'issue_id': id,
                    'message': f'Your issue status changed from {old_status} to {new_status}'
                }
                await supabase_request('POST', 'notifications', payload={'entries': [note]})
        except Exception:
            pass
        # return the updated row
        updated = await get_issue(id)
        return updated
    return None


async def delete_issue(id: str, user) -> Dict[str, Any]:
    issue = await get_issue(id)
    if not issue:
        return {'ok': False, 'status_code': 404, 'error': 'Not found'}
    if str(issue.get('user_id')) != str(user.get('id')):
        return {'ok': False, 'status_code': 403, 'error': 'Forbidden'}
    # handle multiple images cleanup
    imgs = issue.get('images') or []
    for im in imgs:
        if im.get('public_id'):
            try:
                await delete_image(im.get('public_id'))
            except Exception:
                pass
    filters = {'id.eq': id}
    r = await supabase_request('DELETE', 'issues', filters=filters)
    if r.get('status_code') in (200, 204):
        return {'ok': True}
    return {'ok': False, 'error': r.get('data')}
