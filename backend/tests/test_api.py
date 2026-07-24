"""
test_api.py
-----------
Basic API tests using pytest + FastAPI's TestClient.
Run with:  pytest tests/
"""

import io
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from PIL import Image
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def _generate_test_image_bytes():
    """Creates an in-memory dummy JPEG image for upload tests."""
    img = Image.new("RGB", (224, 224), color=(120, 120, 120))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


def test_predict_endpoint():
    image_bytes = _generate_test_image_bytes()
    response = client.post(
        "/api/predict",
        files={"file": ("test_bin.jpg", image_bytes, "image/jpeg")},
        data={"bin_id": "BIN-TEST"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] in ["Empty", "Half Full", "Full"]
    assert 0 <= body["confidence"] <= 1


def test_history_endpoint():
    response = client.get("/api/history?page=1&page_size=5")
    assert response.status_code == 200
    body = response.json()
    assert "results" in body


def test_dashboard_stats():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    body = response.json()
    assert "total_predictions" in body


def test_invalid_file_type_rejected():
    fake_file = io.BytesIO(b"not an image")
    response = client.post(
        "/api/predict",
        files={"file": ("test.txt", fake_file, "text/plain")},
        data={"bin_id": "BIN-TEST"},
    )
    assert response.status_code == 400
