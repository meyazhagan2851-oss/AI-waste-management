"""
predict.py (router)
--------------------
Handles image upload + AI classification in a single request, and
persists the result to the database. This is the core "detect bin
status" API used by the frontend Upload/Prediction page.
"""

import logging
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Prediction
from app.models.schemas import PredictionResponse
from app.services.image_service import save_upload
from app.services.ai_model import predict_image

logger = logging.getLogger("predict_router")
router = APIRouter(prefix="/api/predict", tags=["Prediction"])


@router.post("", response_model=PredictionResponse)
async def predict_bin_status(
    file: UploadFile = File(..., description="Image of the garbage bin"),
    bin_id: str = Form("BIN-001", description="Identifier of the bin being monitored"),
    db: Session = Depends(get_db),
):
    """
    Uploads a bin image, runs AI classification (Empty / Half Full / Full),
    stores the prediction record, and returns the result with a confidence
    score. Sets is_alert=True when the bin is predicted Full so the
    frontend can trigger a notification.
    """
    try:
        # 1. Save image to disk
        unique_filename, full_path = await save_upload(file)

        # 2. Run AI inference
        prediction, confidence = predict_image(full_path)

        # 3. Persist to database
        record = Prediction(
            bin_id=bin_id,
            image_name=unique_filename,
            image_path=full_path,
            prediction=prediction,
            confidence=confidence,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return PredictionResponse(
            id=record.id,
            bin_id=record.bin_id,
            image_name=record.image_name,
            prediction=record.prediction,
            confidence=record.confidence,
            upload_time=record.upload_time,
            is_alert=(record.prediction == "Full"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
