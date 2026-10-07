# backend/app/api/routes/upload.py
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from app.services.upload_service import UploadService

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 1. Create a global variable but leave it empty
_upload_service = None

# 2. Create a dependency function to load it lazily
def get_upload_service() -> UploadService:
    global _upload_service
    if _upload_service is None:
        # This only runs the VERY FIRST time you upload a file
        _upload_service = UploadService()
    return _upload_service

# 3. Inject the service using FastAPI's Depends()
@router.post("/")
async def upload_pdf(
    file: UploadFile = File(...), 
    upload_service: UploadService = Depends(get_upload_service)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    result = upload_service.upload(str(file_path))

    return result