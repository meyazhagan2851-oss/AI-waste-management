"""
dashboard.py (router)
----------------------
Provides aggregate statistics for the Admin Dashboard, and the
current status of each individually tracked bin.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.db_models import Prediction
from app.models.schemas import DashboardStats, BinStatus

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Returns overall counts and averages used for the dashboard summary cards & charts."""
    total = db.query(Prediction).count()

    def count_for(label: str) -> int:
        return db.query(Prediction).filter(Prediction.prediction == label).count()

    avg_confidence = db.query(func.avg(Prediction.confidence)).scalar() or 0.0
    last_record = db.query(Prediction).order_by(Prediction.upload_time.desc()).first()

    return DashboardStats(
        total_predictions=total,
        empty_count=count_for("Empty"),
        half_full_count=count_for("Half Full"),
        full_count=count_for("Full"),
        full_bin_alert_count=count_for("Full"),
        average_confidence=round(float(avg_confidence), 4),
        last_updated=last_record.upload_time if last_record else None,
    )


@router.get("/bins", response_model=list[BinStatus])
def get_bin_statuses(db: Session = Depends(get_db)):
    """
    Returns the latest known status for every distinct bin_id being
    monitored -- this powers the "live bin status" cards on the dashboard.
    """
    distinct_bins = db.query(Prediction.bin_id).distinct().all()
    statuses = []

    for (bin_id,) in distinct_bins:
        latest = (
            db.query(Prediction)
            .filter(Prediction.bin_id == bin_id)
            .order_by(Prediction.upload_time.desc())
            .first()
        )
        if latest:
            statuses.append(
                BinStatus(
                    bin_id=latest.bin_id,
                    latest_prediction=latest.prediction,
                    confidence=latest.confidence,
                    last_checked=latest.upload_time,
                    is_alert=(latest.prediction == "Full"),
                )
            )

    return statuses
