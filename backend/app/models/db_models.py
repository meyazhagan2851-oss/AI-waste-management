"""
db_models.py
------------
SQLAlchemy ORM models representing database tables.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base


class Prediction(Base):
    """
    Stores every prediction made by the AI model, including the
    image reference, predicted class, confidence score, and timestamp.
    This forms the "history" of bin monitoring.
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bin_id = Column(String(50), index=True, default="BIN-001")   # supports multiple bins
    image_name = Column(String(255), nullable=False)
    image_path = Column(String(500), nullable=False)
    prediction = Column(String(50), nullable=False)               # Empty | Half Full | Full
    confidence = Column(Float, nullable=False)                    # 0.0 - 1.0
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
