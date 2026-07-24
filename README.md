# ♻️ AI Smart Waste Management System

An end-to-end, production-ready web application that uses AI image
classification to monitor garbage bin fill levels — **Empty**, **Half
Full**, or **Full** — from uploaded photos, with a real-time admin
dashboard and automatic alerts when a bin needs collection.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/backend-FastAPI-009688)
![React](https://img.shields.io/badge/frontend-React-61DAFB)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 📌 Problem Statement

Manual bin inspection is slow, inconsistent, and reactive — bins often
overflow before anyone notices. This system lets an admin (or an
automated camera feed) upload a bin photo, get an instant AI-based fill
classification with a confidence score, and be alerted the moment any
bin is Full — enabling proactive, data-driven waste collection.

## ✨ Features

- 📊 **Admin Dashboard** — live stats, charts, per-bin status table
- 📤 **Drag-and-drop image upload** with instant preview
- 🤖 **AI classification** (MobileNetV2 transfer learning) with confidence score
- 🗂️ **Prediction history** — searchable, filterable, paginated
- 🚨 **Automatic alerts** (toast notifications) when a bin is Full
- 📱 **Fully responsive**, modern dark-themed UI
- ⚡ **REST API** with auto-generated Swagger docs
- 🔐 Environment-variable driven configuration
- 🧪 Automated backend tests (pytest)

## 🧱 Tech Stack

| Layer      | Technology                                   |
|------------|-----------------------------------------------|
| Frontend   | React.js, React Router, Axios, Chart.js       |
| Backend    | Python, FastAPI, SQLAlchemy                   |
| AI/ML      | TensorFlow (MobileNetV2 transfer learning)    |
| Database   | SQLite (MongoDB-ready, see docs)              |
| Deployment | Render (backend) + Vercel (frontend)          |

## 📁 Folder Structure

```
ai-smart-waste-management/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entrypoint
│   │   ├── config.py               # Env-driven settings
│   │   ├── database.py             # SQLAlchemy session/engine
│   │   ├── models/
│   │   │   ├── db_models.py        # ORM models
│   │   │   └── schemas.py          # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── predict.py          # Upload + AI prediction API
│   │   │   ├── history.py          # History search/filter/delete API
│   │   │   └── dashboard.py        # Aggregate stats API
│   │   ├── services/
│   │   │   ├── ai_model.py         # Model loading + inference
│   │   │   └── image_service.py    # Upload validation + saving
│   │   └── utils/logger.py
│   ├── ai_model/
│   │   ├── model_architecture.py   # CNN (MobileNetV2) definition
│   │   ├── train.py                # Training script
│   │   ├── dataset_prep.py         # Dataset splitting helper
│   │   └── saved_model/            # Trained .h5 goes here
│   ├── dataset/                    # train/ & val/ image folders
│   ├── uploads/                    # Uploaded bin images
│   ├── tests/test_api.py
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
├── frontend/
│   ├── public/index.html
│   ├── src/
│   │   ├── components/             # Navbar, StatCard, PredictionBadge, ...
│   │   ├── pages/                  # Dashboard, UploadPredict, History
│   │   ├── services/api.js         # Axios API layer
│   │   ├── styles/index.css        # Design system / global styles
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── .env.example
└── docs/
    ├── API_DOCUMENTATION.md
    ├── DATABASE_SCHEMA.md
    ├── INSTALLATION.md
    ├── TESTING.md
    ├── DEPLOYMENT.md
    └── VIVA_QUESTIONS.md
```

## 🚀 Quick Start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py                 # → http://localhost:8000

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm start                     # → http://localhost:3000
```

Full step-by-step instructions: [`docs/INSTALLATION.md`](docs/INSTALLATION.md)

> **First run note:** no trained AI model is bundled (weights depend on
> your dataset). The backend automatically uses a heuristic fallback
> classifier until you train one, so the app works end-to-end
> immediately. See below to train a real model.

## 🧠 Training the Model with a Custom Dataset

1. **Collect images** of bins in each state — aim for 150+ images per
   class minimum, ideally 500+, with varied lighting/angles/backgrounds.
2. **Organize** them into:
   ```
   dataset/train/empty/*.jpg
   dataset/train/half_full/*.jpg
   dataset/train/full/*.jpg
   dataset/val/empty/*.jpg  (repeat for val/)
   ```
   Or use the helper: `python ai_model/dataset_prep.py --source raw_images --split 0.8`
3. **Train:**
   ```bash
   cd backend
   python ai_model/train.py --epochs 20 --batch_size 32
   ```
   This uses MobileNetV2 transfer learning + data augmentation, and
   saves the best model to `ai_model/saved_model/waste_classifier.h5`.
4. **Restart the backend** — it auto-detects and loads the trained model.
   Confirm via `GET /api/health` → `"ai_model": "trained"`.

## 📡 API Overview

| Method | Endpoint                     | Description                        |
|--------|-------------------------------|--------------------------------------|
| POST   | `/api/predict`                | Upload image → get AI classification |
| GET    | `/api/history`                | Paginated/searchable prediction log  |
| DELETE | `/api/history/{id}`           | Delete a history record              |
| GET    | `/api/dashboard/stats`        | Aggregate counts & averages          |
| GET    | `/api/dashboard/bins`         | Latest status per bin                |
| GET    | `/api/health`                 | Health + AI model status             |

Full request/response examples: [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md)

## 🗄️ Database Schema

See [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) — one table
(`predictions`) storing `id, bin_id, image_name, prediction, confidence,
upload_time`.

## 🧪 Testing

```bash
cd backend && pytest tests/ -v
```
See [`docs/TESTING.md`](docs/TESTING.md) for the manual QA checklist too.

## ☁️ Deployment

Deploy backend to **Render** and frontend to **Vercel** — full guide in
[`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## 🔮 Future Enhancements

- Real-time video stream monitoring (RTSP camera feeds) instead of
  single-image uploads
- YOLOv8 object detection to localize the bin and estimate fill volume
  more precisely (not just whole-image classification)
- Email/SMS push notifications (Twilio, SendGrid) in addition to
  in-app toast alerts
- Role-based authentication (admin vs. viewer) with JWT
- Route optimization for collection trucks based on live Full-bin data
- Multi-tenant support (separate organizations/cities)
- Edge deployment on Raspberry Pi + camera per physical bin
- Model retraining pipeline with human-in-the-loop correction of
  misclassified predictions

## ⚖️ AI Ethics Considerations

- **Bias & fairness:** the model should be trained on bins from diverse
  locations/contexts to avoid systematic misclassification in
  under-represented neighborhoods, which could lead to inequitable
  service (e.g. consistently under-servicing certain areas).
- **Transparency:** confidence scores are always shown to the admin
  rather than hidden, so low-certainty predictions can be
  human-verified instead of auto-trusted.
- **Privacy:** uploaded images should avoid capturing identifiable
  people or private property in the background; production deployments
  should crop/blur non-bin regions and follow local data protection
  regulations for any stored imagery.
- **Accountability:** automated "Full" alerts should augment, not fully
  replace, human judgment — especially early on, until real-world
  accuracy is validated against ground truth.
- **Environmental intent:** the system's stated purpose (efficient
  collection, reduced overflow) should be the actual outcome measured
  post-deployment, not assumed.

## 📄 License

MIT — free to use, modify, and extend for academic or commercial projects.
