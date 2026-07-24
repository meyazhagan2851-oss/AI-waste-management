# Database Schema

The system uses **SQLite** by default (zero-config, file-based, perfect for
demos and small deployments). The schema is defined via SQLAlchemy ORM in
`backend/app/models/db_models.py` and can be pointed at PostgreSQL/MySQL/MongoDB
in production simply by changing `DATABASE_URL` in `.env`.

## Table: `predictions`

| Column       | Type              | Constraints                  | Description                                   |
|--------------|-------------------|-------------------------------|------------------------------------------------|
| id           | INTEGER           | PRIMARY KEY, AUTOINCREMENT   | Unique record identifier                       |
| bin_id       | VARCHAR(50)       | INDEXED, default "BIN-001"   | Identifier of the physical bin monitored        |
| image_name   | VARCHAR(255)      | NOT NULL                     | Unique stored filename of the uploaded image    |
| image_path   | VARCHAR(500)      | NOT NULL                     | Full path to the image on disk                  |
| prediction   | VARCHAR(50)       | NOT NULL                     | One of: `Empty`, `Half Full`, `Full`            |
| confidence   | FLOAT             | NOT NULL                     | Model confidence score, range 0.0 - 1.0         |
| upload_time  | DATETIME          | default NOW()                | Timestamp the record was created                |

### SQL equivalent (for reference / manual creation)

```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bin_id VARCHAR(50) DEFAULT 'BIN-001',
    image_name VARCHAR(255) NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    prediction VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_predictions_bin_id ON predictions(bin_id);
```

## Switching to MongoDB

If you prefer MongoDB, the equivalent document shape is:

```json
{
  "_id": "ObjectId",
  "bin_id": "BIN-001",
  "image_name": "20260723_ab12cd34.jpg",
  "image_path": "uploads/20260723_ab12cd34.jpg",
  "prediction": "Full",
  "confidence": 0.94,
  "upload_time": "2026-07-23T10:15:00Z"
}
```

To switch: install `pymongo` (already in `requirements.txt`), replace the
SQLAlchemy session logic in `app/database.py` with a `pymongo.MongoClient`
connection, and adapt the router functions in `app/routers/` to use
`collection.insert_one()` / `collection.find()` instead of ORM queries. The
Pydantic schemas in `app/models/schemas.py` remain unchanged either way,
since they define the API contract, not the storage layer.

## Entity Relationship Diagram (conceptual)

```
+-------------------+
|   predictions     |
+-------------------+
| id (PK)           |
| bin_id            |
| image_name        |
| image_path        |
| prediction        |
| confidence        |
| upload_time       |
+-------------------+
```

This is intentionally a single-table design — the system tracks predictions
as independent events, and "bin status" is derived (the latest prediction
per `bin_id`) rather than stored redundantly. This keeps the schema simple
and avoids update anomalies.
