# Installation Guide

## Prerequisites

- Python 3.10 – 3.11 (TensorFlow 2.16 does not yet support 3.12 on all platforms)
- Node.js 18+ and npm
- Git

## 1. Clone / Extract the Project

```bash
cd ai-smart-waste-management
```

## 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env if needed (defaults work out of the box with SQLite)

# Run the server
python run.py
```

The API will be available at **http://localhost:8000** and interactive
docs at **http://localhost:8000/docs**.

> **Note on the AI model:** the project ships without a pre-trained
> `.h5` file (trained weights depend on your own dataset). Until you
> train one (see "Training the Model" below), the backend automatically
> uses a lightweight heuristic fallback classifier so the full app is
> runnable and demoable immediately. Check `GET /api/health` — it
> reports `"ai_model": "trained"` or `"heuristic_fallback"`.

## 3. Frontend Setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Edit REACT_APP_API_BASE_URL if your backend runs on a different host/port

# Run the development server
npm start
```

The app will open at **http://localhost:3000**.

## 4. Training the AI Model (Optional but Recommended)

```bash
cd backend

# 1. Organize your dataset (or use dataset_prep.py to auto-split a flat folder)
python ai_model/dataset_prep.py --source /path/to/raw_labeled_images --split 0.8

# Expected structure after this step:
#   dataset/train/empty/*.jpg
#   dataset/train/half_full/*.jpg
#   dataset/train/full/*.jpg
#   dataset/val/empty/*.jpg  ... etc.

# 2. Train
python ai_model/train.py --epochs 20 --batch_size 32

# 3. The trained model is saved automatically to:
#    ai_model/saved_model/waste_classifier.h5
# Restart the backend server to load it.
```

See `README.md` → "Training the Model with a Custom Dataset" for full
guidance on collecting a good dataset.

## 5. Verify Everything Works

1. Visit `http://localhost:3000` — you should see the Dashboard.
2. Go to **Upload & Predict**, upload a bin photo, and confirm you get
   back a prediction with a confidence score.
3. Go to **History** and confirm the record appears, is searchable, and
   filterable.
4. Upload an image that gets classified as "Full" and confirm a toast
   alert appears.

## Troubleshooting

| Issue                                   | Fix                                                              |
|------------------------------------------|-------------------------------------------------------------------|
| `ModuleNotFoundError: fastapi`           | Ensure your virtual environment is activated before `pip install` |
| CORS errors in browser console           | Check `ALLOWED_ORIGINS` in backend `.env` includes your frontend URL |
| Frontend can't reach backend             | Check `REACT_APP_API_BASE_URL` in frontend `.env`, restart `npm start` after editing |
| TensorFlow install fails                 | Use Python 3.10/3.11; on Apple Silicon use `tensorflow-macos` instead |
| Images not showing in History            | Confirm `uploads/` directory exists and backend has write permission |
