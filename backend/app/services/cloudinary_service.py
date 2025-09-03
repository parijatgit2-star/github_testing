from typing import Dict, Optional
import httpx
from ..config import settings


async def upload_image(file_path: str, folder: str = 'issues') -> Dict[str, Optional[str]]:
    """Upload a file to Cloudinary using the REST API and return secure_url and public_id.
    Uses Cloudinary API key/secret for authentication.
    """
    url = f"https://api.cloudinary.com/v1_1/{settings.CLOUDINARY_CLOUD_NAME}/image/upload"
    auth = (settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET)

    # Read file bytes
    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    files = {'file': (file_path, file_bytes)}
    data = {'folder': folder}

    async with httpx.AsyncClient() as client:
        r = await client.post(url, auth=auth, files=files, data=data, timeout=30)
        try:
            body = r.json()
        except Exception:
            body = {'text': r.text}
    return {'secure_url': body.get('secure_url'), 'public_id': body.get('public_id')}


async def delete_image(public_id: str) -> Dict:
    """Delete image by public_id using Cloudinary API."""
    url = f"https://api.cloudinary.com/v1_1/{settings.CLOUDINARY_CLOUD_NAME}/resources/image/upload"
    auth = (settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET)
    params = {'public_ids[]': public_id}
    async with httpx.AsyncClient() as client:
        r = await client.delete(url, auth=auth, params=params)
        try:
            return r.json()
        except Exception:
            return {'text': r.text}
