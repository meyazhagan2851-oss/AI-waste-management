"""
main.py
-------
FastAPI application entrypoint for the AI Smart Waste Management System.
Wires together configuration, database, routers, and middleware.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.utils.logger import setup_logging
from app.routers import predict, history, dashboard
from app.services.ai_model import is_using_trained_model

setup_logging()
logger = logging.getLogger("main")

app = FastAPI(
    title=settings.APP_NAME,
    description="REST API for AI-powered garbage bin monitoring (Empty / Half Full / Full).",
    version="1.0.0",
)

# ---- CORS ----
# Allows the React frontend (running on a different origin) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Static files ----
# Serves uploaded images directly, e.g. GET /uploads/<filename>
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ---- Routers ----
app.include_router(predict.router)
app.include_router(history.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def on_startup():
    """Runs once when the server starts: creates DB tables and warms up the AI model."""
    init_db()
    logger.info("Database initialized.")
    using_trained = is_using_trained_model()
    if using_trained:
        logger.info("AI model status: using TRAINED model.")
    else:
        logger.warning(
            "AI model status: using HEURISTIC FALLBACK (no trained model found). "
            "Train a model with ai_model/train.py for real predictions."
        )


@app.get("/", tags=["Health"])
def root():
    """Basic health check / welcome endpoint."""
    return {
        "message": f"{settings.APP_NAME} API is running.",
        "docs": "/docs",
        "status": "ok",
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    """Detailed health check, including AI model status."""
    return {
        "status": "healthy",
        "ai_model": "trained" if is_using_trained_model() else "heuristic_fallback",
        "environment": settings.APP_ENV,
    }
