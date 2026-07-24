# Viva Questions & Answers

### 1. What problem does this project solve?
It automates garbage bin monitoring by using AI image classification to
detect fill level (Empty, Half Full, Full) from a photo, instead of
relying on manual inspection rounds — enabling smarter collection
scheduling and reducing overflow incidents.

### 2. Why did you choose MobileNetV2 for the model?
MobileNetV2 is a lightweight, efficient CNN designed for mobile/edge
deployment. It performs well with transfer learning on small custom
datasets, trains faster than larger architectures like ResNet50, and is
suitable if the system is later deployed on low-power devices (e.g. a
Raspberry Pi camera at the bin itself).

### 3. What is transfer learning, and why use it here?
Transfer learning reuses a model already trained on a large dataset
(ImageNet) and adapts it to a new, smaller task. Training a CNN from
scratch would need thousands of labeled bin images; transfer learning
lets the model reuse general visual features (edges, textures, shapes)
and only learn the bin-specific classification head, requiring far less
data and training time.

### 4. Why FastAPI instead of Flask?
FastAPI offers automatic OpenAPI/Swagger documentation, built-in request
validation via Pydantic, native async support (useful for I/O-bound
operations like file uploads), and better performance than Flask's
default WSGI model — all while remaining just as easy to write.

### 5. How does the system store and retrieve prediction history?
Every prediction is saved as a row in the `predictions` table (id,
bin_id, image_name, prediction, confidence, upload_time) via SQLAlchemy
ORM. The History API supports pagination, text search, and status
filtering using SQL `WHERE`/`LIKE` clauses and `LIMIT`/`OFFSET`.

### 6. How are "Full bin" alerts implemented?
Whenever a prediction resolves to "Full", the API response sets
`is_alert: true`. The frontend Dashboard polls bin statuses every 15
seconds and fires a toast notification the first time each bin is seen
as Full in the current session — this can be extended to email/SMS/push
notifications in production.

### 7. What happens if no trained model is available?
The `ai_model.py` service falls back to a heuristic classifier based on
grayscale edge density (a proxy for visual clutter) so the entire
application remains runnable and demoable before any training data has
been collected — a practical decision for prototyping and for grading
without requiring GPU access.

### 8. How would you improve prediction accuracy?
Collect a larger, more diverse dataset (varied lighting, angles, bin
types); use data augmentation (already included: flips, rotation, zoom,
brightness); fine-tune deeper layers of the base model; consider object
detection (YOLOv8) to also localize the bin opening and estimate volume
more precisely rather than just classifying the whole image.

### 9. Why store the confidence score, and how is it used?
Confidence quantifies how certain the model is. It's shown to the admin
as a percentage/progress bar so they can judge trustworthiness of a
prediction (e.g. flag low-confidence Full predictions for manual
verification before dispatching a truck).

### 10. How does the system handle scaling to many bins?
Each prediction is tagged with a `bin_id`. The Dashboard's `/bins`
endpoint derives the latest status per distinct `bin_id`, so the same
schema and pipeline scale to any number of physically distinct bins
without structural changes — you simply pass a different `bin_id` per
camera/location when calling the predict API.

### 11. What security considerations exist in the current design?
File type validation, file size limits, and CORS restriction to known
frontend origins. For production: add authentication (JWT) on
admin-only endpoints (delete, dashboard), rate limiting on `/api/predict`
to prevent abuse, and virus/malware scanning of uploaded files.

### 12. How would you deploy this to production?
Backend on Render (or any ASGI-compatible host) with a managed
PostgreSQL database and persistent object storage for images; frontend
as a static build on Vercel; environment variables for all
secrets/config; HTTPS enforced on both ends. Full steps are in
`docs/DEPLOYMENT.md`.

### 13. Why separate Pydantic schemas from SQLAlchemy models?
It decouples the API's public contract from the internal database
representation, allowing internal fields to change (or hide fields like
`image_path`) without breaking the API, and enables FastAPI's automatic
request/response validation and documentation generation.

### 14. What testing strategy did you use?
Backend: pytest with FastAPI's TestClient covering health, prediction,
history, and validation error paths. Frontend: a manual QA checklist
covering responsive layout, upload flows, filtering, and alert behavior
(see `docs/TESTING.md`).

### 15. What are the system's current limitations?
Single-image classification only (no live video stream); no built-in
authentication; SQLite is not ideal for concurrent production writes at
scale; heuristic fallback is not a substitute for a properly trained
model; no automated notification channel (email/SMS) yet, only in-app
toast alerts.
