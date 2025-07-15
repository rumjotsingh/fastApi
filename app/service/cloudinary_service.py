import cloudinary.uploader
from typing import Optional
from fastapi import UploadFile
import asyncio

async def upload_image(file: UploadFile, folder: Optional[str] = None) -> str:
    """
    Upload a file to Cloudinary and return the secure URL.
    Runs in a thread to avoid blocking the event loop.
    """
    def _upload():
        return cloudinary.uploader.upload(
            file.file,
            folder=folder
        )
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _upload)
    return result["secure_url"]
