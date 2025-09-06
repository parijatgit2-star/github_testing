from typing import Dict
from ..db.supabase_client import supabase_request


async def answer_query(question: str) -> Dict:
    """Finds an answer to a question using simple keyword matching against FAQs.

    This function attempts to find a relevant answer by searching for the
    question text and keywords within the pre-existing FAQs stored in the
    database.

    Args:
        question: The user's question string.

    Returns:
        A dictionary containing the answer, or a default message if no
        relevant answer is found.
    """
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
    """Performs a basic check for spam or unwanted content in a string.

    This function uses a simple list of banned keywords to flag text.
    It is not a sophisticated spam filter.

    Args:
        text: The input text to check.

    Returns:
        True if a banned keyword is found, False otherwise.
    """
    banned = ['spam', 'buy now', 'free', 'http', 'www.', 'offensive']
    t = (text or '').lower()
    return any(b in t for b in banned)
