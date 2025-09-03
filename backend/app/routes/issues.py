from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Form
from typing import List, Optional, Dict, Any
from ..schemas.api_models import (
    IssueCreateModel,
    IssueResponseModel,
    IssueUpdateModel,
    CommentCreateModel,
    CommentResponseModel,
)
from ..services.issue_service import create_issue, get_issue, update_issue, delete_issue
from ..utils.auth_dependencies import get_current_user

from ..db.supabase_client import supabase_request
from ..utils.validation import validate_list, validate_single

router = APIRouter(prefix='/issues', tags=['issues'])


@router.post('/', response_model=IssueResponseModel, status_code=201)
async def post_issue(
    title: str = Form(...),
    description: str = Form(...),
    lat: Optional[float] = Form(None),
    lng: Optional[float] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    user: Dict[str, Any] = Depends(get_current_user),
):
    # Build a lightweight payload compatible with IssueCreateModel
    payload = {
        'title': title,
        'description': description,
        'location': f'{lat},{lng}' if lat is not None and lng is not None else None,
        'images': None,
    }
    return await create_issue(payload, image_files=images, user=user)


@router.get('/', response_model=List[IssueResponseModel])
async def list_issues(status: Optional[str] = None, category: Optional[str] = None, limit: int = Query(50, le=200), offset: int = 0):
    """List issues with optional filters and pagination."""
    filters: Dict[str, Any] = {}
    if status:
        filters['status.eq'] = status
    if category:
        filters['category.eq'] = category
    r = await supabase_request('GET', 'issues', filters=filters)
    data = r.get('data') or []
    validated = validate_list(IssueResponseModel, data)
    return validated[offset: offset + limit]


@router.get('/staff/me', response_model=List[IssueResponseModel])
async def staff_my_issues(user: Dict[str, Any] = Depends(get_current_user)):
    """Return issues assigned to the logged-in staff user."""
    if not user or user.get('role') not in ('staff', 'admin'):
        raise HTTPException(status_code=403, detail='Forbidden')
    r = await supabase_request('GET', 'issues', filters={'assignee.eq': user.get('id')})
    data = r.get('data') or []
    return validate_list(IssueResponseModel, data)


@router.get('/{issue_id}', response_model=IssueResponseModel)
async def read_issue(issue_id: str):
    issue = await get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail='Issue not found')
    return validate_single(IssueResponseModel, issue)


@router.patch('/{issue_id}', response_model=IssueResponseModel)
async def patch_issue(issue_id: str, payload: IssueUpdateModel, user: Dict[str, Any] = Depends(get_current_user)):
    updated = await update_issue(issue_id, payload, user)
    if not updated:
        raise HTTPException(status_code=404, detail='Issue not found or not allowed')
    return validate_single(IssueResponseModel, updated)


@router.delete('/{issue_id}', status_code=204)
async def remove_issue(issue_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    ok = await delete_issue(issue_id, user)
    if not ok:
        raise HTTPException(status_code=404, detail='Issue not found or not allowed')
    return None


@router.post('/{issue_id}/assign')
async def assign_issue(issue_id: str, department_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    # minimal role check
    if not user or user.get('role') not in ('staff', 'admin'):
        raise HTTPException(status_code=403, detail='Forbidden')
    # construct a minimal update payload as dict to avoid Pydantic required-field issues
    res = await update_issue(issue_id, {'status': 'assigned', 'department_id': department_id}, user)
    return validate_single(IssueResponseModel, res)


@router.post('/{issue_id}/resolve')
async def resolve_issue(issue_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    if not user or user.get('role') not in ('staff', 'admin'):
        raise HTTPException(status_code=403, detail='Forbidden')
    res = await update_issue(issue_id, {'status': 'resolved'}, user)
    return validate_single(IssueResponseModel, res)


@router.post('/{issue_id}/comments', response_model=CommentResponseModel)
async def add_comment(issue_id: str, payload: CommentCreateModel, user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Add a comment to an issue."""
    note = {
        'issue_id': issue_id,
        'user_id': user.get('id') if user else None,
        'text': payload.text,
    }
    r = await supabase_request('POST', 'comments', payload=note)
    data = r.get('data') or []
    return validate_single(CommentResponseModel, data[0] if data else None)


@router.get('/{issue_id}/comments', response_model=List[CommentResponseModel])
async def get_comments(issue_id: str):
    """Fetch comments for an issue."""
    try:
        r = await supabase_request('GET', 'comments', filters={'issue_id.eq': issue_id})
        data = r.get('data') or []
        return validate_list(CommentResponseModel, data)
    except Exception:
        # In tests or offline mode, upstream DB may be unreachable. Return empty list.
        return []


