"""
image_service.py
-----------------
Handles image validation and persistence to disk for uploaded bin photos.
"""

import os
import uuid
from datetime import datetime
from fastapi import UploadFile, HTTPException

from app.config import settings


def validate_image(file: UploadFile):
    """Validates file extension and size before processing."""
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Allowed types: {settings.allowed_extensions_list}",
        )


async def save_upload(file: UploadFile) -> tuple[str, str]:
    """
    Saves the uploaded file to the UPLOAD_DIR with a unique filename to
    avoid collisions, enforcing the max size limit while streaming to disk.

    Returns:
        (unique_filename, full_path)
    """
    validate_image(file)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    ext = file.filename.split(".")[-1].lower()
    unique_filename = f"{timestamp}_{unique_id}.{ext}"
    full_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    size = 0

    with open(full_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # read in 1MB chunks
            size += len(chunk)
            if size > max_bytes:
                buffer.close()
                os.remove(full_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max allowed size is {settings.MAX_UPLOAD_SIZE_MB}MB.",
                )
            buffer.write(chunk)

    return unique_filename, full_path
