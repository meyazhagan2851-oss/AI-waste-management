# Testing Guide

## Backend Tests (pytest)

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

`tests/test_api.py` covers:
- Health check endpoint
- Successful image upload + prediction
- Rejection of invalid file types
- History listing with pagination
- Dashboard statistics endpoint

## Manual API Testing (via Swagger UI)

1. Start the backend: `python run.py`
2. Open `http://localhost:8000/docs`
3. Expand `POST /api/predict`, click "Try it out", upload a test image,
   set a `bin_id`, and execute.
4. Confirm the response includes `prediction`, `confidence`, and `is_alert`.

## Manual API Testing (via cURL)

```bash
# Predict
curl -X POST http://localhost:8000/api/predict \
  -F "file=@sample_bin.jpg" -F "bin_id=BIN-001"

# History
curl "http://localhost:8000/api/history?page=1&page_size=5"

# Dashboard stats
curl http://localhost:8000/api/dashboard/stats
```

## Frontend Manual Testing Checklist

- [ ] Dashboard loads stat cards and charts without errors
- [ ] Navbar collapses correctly on mobile widths (< 768px)
- [ ] Upload page accepts drag-and-drop and click-to-browse
- [ ] Invalid file types show an inline error, not a crash
- [ ] Prediction result shows confidence bar animating to the correct %
- [ ] A "Full" prediction triggers a red toast alert
- [ ] History page search filters results as expected
- [ ] History page status filter (Empty/Half Full/Full) works
- [ ] Pagination Next/Previous buttons disable correctly at boundaries
- [ ] Deleting a history record removes it and shows a confirmation toast

## Suggested Test Dataset for Manual QA

If you don't have real bin photos yet, you can quickly test the pipeline
using any three folders of contrasting images (e.g. a mostly-empty box,
a partially cluttered surface, a very cluttered/full surface) — the
heuristic fallback classifier responds to visual "busyness", so contrast
in clutter/darkness will produce different classes even before you've
trained a real model.

## Load/Performance Testing (optional)

```bash
# Using Apache Bench to test predict endpoint throughput
ab -n 50 -c 5 -p sample_bin.jpg -T 'image/jpeg' http://localhost:8000/api/predict
```

## Continuous Integration

A minimal GitHub Actions workflow (`.github/workflows/backend-tests.yml`)
can run `pytest` on every push:

```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest tests/ -v
```
