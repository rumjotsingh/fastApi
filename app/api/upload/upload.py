from fastapi import APIRouter, UploadFile, File, HTTPException
from app.service.cloudinary_service import upload_image

router = APIRouter()

@router.post("/", summary="Upload file to Cloudinary")
async def upload_file(file: UploadFile = File(...)):
    try:
        url = await upload_image(file, folder="user_uploads")
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
