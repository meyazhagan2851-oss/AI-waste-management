"""
schemas.py
----------
Pydantic schemas used for request validation and response serialization.
Keeping these separate from the ORM models follows the
"never expose your DB model directly" best practice.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class PredictionResponse(BaseModel):
    """Response returned immediately after an image is classified."""
    id: int
    bin_id: str
    image_name: str
    prediction: str
    confidence: float = Field(..., ge=0, le=1)
    upload_time: datetime
    is_alert: bool  # True if prediction == "Full"

    class Config:
        from_attributes = True  # allows creation directly from ORM objects


class PredictionHistoryItem(BaseModel):
    id: int
    bin_id: str
    image_name: str
    prediction: str
    confidence: float
    upload_time: datetime

    class Config:
        from_attributes = True


class PredictionHistoryResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[PredictionHistoryItem]


class DashboardStats(BaseModel):
    total_predictions: int
    empty_count: int
    half_full_count: int
    full_count: int
    full_bin_alert_count: int
    average_confidence: float
    last_updated: Optional[datetime] = None


class BinStatus(BaseModel):
    bin_id: str
    latest_prediction: str
    confidence: float
    last_checked: datetime
    is_alert: bool
