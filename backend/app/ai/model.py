from typing import Dict
from ..db.supabase_client import supabase_request


async def answer_query(question: str) -> Dict:
    # Simple keyword matching against FAQ table
    r = await supabase_request('GET', 'faq')
    faqs = r.get('data') or []
    q = (question or '').lower()
    for item in faqs:
        if item.get('question') and item.get('question').lower() in q:
            return {'answer': item.get('answer')}
    # fallback: return first similar by keyword
    for item in faqs:
        if any(k in q for k in (item.get('question') or '').lower().split()):
            return {'answer': item.get('answer')}
    return {'answer': 'Sorry, I do not know the answer to that yet.'}


def detect_unwanted_submission(text: str) -> bool:
    banned = ['spam', 'buy now', 'free', 'http', 'www.', 'offensive']
    t = (text or '').lower()
    return any(b in t for b in banned)
