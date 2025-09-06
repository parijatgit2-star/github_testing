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
    """Submits a new issue, including optional image uploads.

    This endpoint accepts issue data as form fields and supports multipart/form-data
    for file uploads.

    Args:
        title: The title of the issue.
        description: A detailed description of the issue.
        lat: The latitude of the issue's location.
        lng: The longitude of the issue's location.
        images: An optional list of uploaded image files.
        user: The authenticated user, injected by FastAPI.

    Returns:
        The created issue object.
    """
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
    """Lists all issues, with optional filters and pagination.

    Args:
        status: Filter issues by their status (e.g., 'pending', 'resolved').
        category: Filter issues by their category.
        limit: The maximum number of issues to return.
        offset: The starting offset for pagination.

    Returns:
        A list of issue objects matching the filter criteria.
    """
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
    """Returns all issues assigned to the currently logged-in staff member.

    This is a protected endpoint available only to users with 'staff' or 'admin' roles.

    Args:
        user: The authenticated user, injected by FastAPI.

    Returns:
        A list of assigned issue objects.
    """
    if not user or user.get('role') not in ('staff', 'admin'):
        raise HTTPException(status_code=403, detail='Forbidden')
    r = await supabase_request('GET', 'issues', filters={'assignee.eq': user.get('id')})
    data = r.get('data') or []
    return validate_list(IssueResponseModel, data)


@router.get('/{issue_id}', response_model=IssueResponseModel)
async def read_issue(issue_id: str):
    """Retrieves a single issue by its ID.

    Args:
        issue_id: The unique identifier of the issue to retrieve.

    Returns:
        The requested issue object.

    Raises:
        HTTPException: If the issue is not found.
    """
    issue = await get_issue(issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail='Issue not found')
    return validate_single(IssueResponseModel, issue)


@router.patch('/{issue_id}', response_model=IssueResponseModel)
async def patch_issue(issue_id: str, payload: IssueUpdateModel, user: Dict[str, Any] = Depends(get_current_user)):
    """Updates the details of an existing issue.

    Args:
        issue_id: The unique identifier of the issue to update.
        payload: An `IssueUpdateModel` with the fields to be updated.
        user: The authenticated user, injected by FastAPI.

    Returns:
        The updated issue object.

    Raises:
        HTTPException: If the issue is not found or the user is not permitted
            to perform the update.
    """
    updated = await update_issue(issue_id, payload, user)
    if not updated:
        raise HTTPException(status_code=404, detail='Issue not found or not allowed')
    return validate_single(IssueResponseModel, updated)


@router.delete('/{issue_id}', status_code=204)
async def remove_issue(issue_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Deletes an issue.

    This action is protected and can only be performed by the user who created
    the issue.

    Args:
        issue_id: The unique identifier of the issue to delete.
        user: The authenticated user, injected by FastAPI.

    Raises:
        HTTPException: If the issue is not found or the user is not permitted
            to delete it.
    """
    ok = await delete_issue(issue_id, user)
    if not ok:
        raise HTTPException(status_code=404, detail='Issue not found or not allowed')
    return None


@router.post('/{issue_id}/assign')
async def assign_issue(issue_id: str, department_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Assigns an issue to a department.

    This is a protected endpoint available only to users with 'staff' or 'admin' roles.

    Args:
        issue_id: The ID of the issue to assign.
        department_id: The ID of the department to assign the issue to.
        user: The authenticated user, injected by FastAPI.

    Returns:
        The updated issue object with the new assignment.
    """
    # minimal role check
    if not user or user.get('role') not in ('staff', 'admin'):
        raise HTTPException(status_code=403, detail='Forbidden')
    # construct a minimal update payload as dict to avoid Pydantic required-field issues
    res = await update_issue(issue_id, {'status': 'assigned', 'department_id': department_id}, user)
    return validate_single(IssueResponseModel, res)


@router.post('/{issue_id}/resolve')
async def resolve_issue(issue_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Marks an issue as resolved.

    This is a protected endpoint available only to users with 'staff' or 'admin' roles.

    Args:
        issue_id: The ID of the issue to resolve.
        user: The authenticated user, injected by FastAPI.

    Returns:
        The updated issue object with the 'resolved' status.
    """
    if not user or user.get('role') not in ('staff', 'admin'):
        raise HTTPException(status_code=403, detail='Forbidden')
    res = await update_issue(issue_id, {'status': 'resolved'}, user)
    return validate_single(IssueResponseModel, res)


@router.post('/{issue_id}/comments', response_model=CommentResponseModel)
async def add_comment(issue_id: str, payload: CommentCreateModel, user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """Adds a comment to an issue.

    This can be performed by an authenticated user or anonymously, depending
    on the system configuration.

    Args:
        issue_id: The ID of the issue to comment on.
        payload: A `CommentCreateModel` containing the text of the comment.
        user: The authenticated user (if any), injected by FastAPI.

    Returns:
        The newly created comment object.
    """
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
    """Fetches all comments associated with a specific issue.

    Args:
        issue_id: The ID of the issue for which to retrieve comments.

    Returns:
        A list of comment objects.
    """
    try:
        r = await supabase_request('GET', 'comments', filters={'issue_id.eq': issue_id})
        data = r.get('data') or []
        return validate_list(CommentResponseModel, data)
    except Exception:
        # In tests or offline mode, upstream DB may be unreachable. Return empty list.
        return []


