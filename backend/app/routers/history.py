"""
history.py (router)
--------------------
Provides paginated, searchable, filterable access to past predictions,
plus an endpoint to serve stored images and delete records.
"""

import os
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.database import get_db
from app.models.db_models import Prediction
from app.models.schemas import PredictionHistoryResponse, PredictionHistoryItem

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("", response_model=PredictionHistoryResponse)
def get_history(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by image name or bin id"),
    prediction: Optional[str] = Query(None, description="Filter by class: Empty | Half Full | Full"),
    bin_id: Optional[str] = Query(None, description="Filter by specific bin"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    """
    Returns paginated prediction history with optional search & filters.
    """
    query = db.query(Prediction)

    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            or_(Prediction.image_name.ilike(like_pattern), Prediction.bin_id.ilike(like_pattern))
        )

    if prediction:
        query = query.filter(Prediction.prediction == prediction)

    if bin_id:
        query = query.filter(Prediction.bin_id == bin_id)

    total = query.count()

    records = (
        query.order_by(Prediction.upload_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PredictionHistoryResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=[PredictionHistoryItem.model_validate(r) for r in records],
    )


@router.get("/image/{filename}")
def get_image(filename: str):
    """Serves a stored bin image by filename (used to preview history entries)."""
    from app.config import settings
    path = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)


@router.delete("/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """Deletes a single prediction record (admin cleanup use case)."""
    record = db.query(Prediction).filter(Prediction.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": f"Record {record_id} deleted successfully"}
