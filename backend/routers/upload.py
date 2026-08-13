import os
import uuid
import aiofiles
import structlog
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from config import get_settings

log = structlog.get_logger()
router = APIRouter()
settings = get_settings()

ALLOWED_EXTENSIONS = {".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file for transcription.
    Returns a job_id to be used in subsequent /transcribe calls.
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    job_id = str(uuid.uuid4())
    dest_path = Path(settings.UPLOAD_DIR) / f"{job_id}{ext}"

    size = 0
    too_large = False
    async with aiofiles.open(dest_path, "wb") as out:
        while chunk := await file.read(1024 * 1024):  # 1 MB chunks
            size += len(chunk)
            if size > MAX_BYTES:
                too_large = True
                break
            await out.write(chunk)

    if too_large:
        dest_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    log.info("audio_uploaded", job_id=job_id, filename=file.filename, size_bytes=size)
    return {"job_id": job_id, "filename": file.filename, "size_bytes": size}
