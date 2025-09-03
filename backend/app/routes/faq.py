from fastapi import APIRouter
from ..db.supabase_client import supabase_request
from ..ai.model import answer_query

router = APIRouter(prefix='/faq', tags=['faq'])


@router.get('/')
async def get_faqs():
    r = await supabase_request('GET', 'faq')
    return r.get('data')


@router.post('/ask')
async def ask_question(payload: dict):
    q = payload.get('question')
    return await answer_query(q)

