from typing import Dict, Optional
import httpx
from ..config import settings


async def upload_image(file_path: str, folder: str = 'issues') -> Dict[str, Optional[str]]:
    """Uploads an image file to Cloudinary.

    This function reads a file from the local filesystem and uploads it to a
    specified folder in Cloudinary using the Cloudinary REST API. It
    authenticates using credentials from the application settings.

    Args:
        file_path: The local path to the image file to upload.
        folder: The name of the folder in Cloudinary to upload the image to.
            Defaults to 'issues'.

    Returns:
        A dictionary containing the 'secure_url' and 'public_id' of the
        uploaded image. Returns None for values if the upload fails.
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
    """Deletes an image from Cloudinary using its public ID.

    Args:
        public_id: The unique public identifier of the image in Cloudinary.

    Returns:
        A dictionary containing the result of the deletion operation from
        the Cloudinary API.
    """
    url = f"https://api.cloudinary.com/v1_1/{settings.CLOUDINARY_CLOUD_NAME}/resources/image/upload"
    auth = (settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET)
    params = {'public_ids[]': public_id}
    async with httpx.AsyncClient() as client:
        r = await client.delete(url, auth=auth, params=params)
        try:
            return r.json()
        except Exception:
            return {'text': r.text}
