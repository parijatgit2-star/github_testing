from fastapi import APIRouter
from typing import List
from ..db.supabase_client import supabase_request

router = APIRouter(prefix='/departments', tags=['departments'])

@router.get('/', response_model=List[dict])
async def list_departments():
    """
    Retrieves a list of all departments.
    """
    r = await supabase_request('GET', 'departments')
    return r.get('data') or []
