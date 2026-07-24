# Deployment Guide (Render + Vercel)

This guide deploys the **backend (FastAPI)** to **Render** and the
**frontend (React)** to **Vercel**.

---

## Part 1: Deploy Backend to Render

1. Push the `backend/` folder to a GitHub repository.
2. In Render, click **New → Web Service** and connect your repo.
3. Configure:
   - **Root Directory:** `backend`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (Render dashboard → Environment):
   ```
   APP_ENV=production
   DEBUG=False
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   DATABASE_URL=sqlite:///./waste_management.db
   UPLOAD_DIR=uploads
   MODEL_PATH=ai_model/saved_model/waste_classifier.h5
   ```
5. **Persistent storage note:** Render's free tier filesystem is
   ephemeral — uploaded images and the SQLite file will reset on
   redeploy. For production, attach a Render **Disk** (Settings → Disks)
   mounted at `/opt/render/project/src/backend/uploads` and point
   `DATABASE_URL` at a managed **Render PostgreSQL** instance instead of
   SQLite for durability.
6. Deploy. Your API will be live at `https://<your-service>.onrender.com`.
7. Verify: visit `https://<your-service>.onrender.com/docs`.

### Optional: switch to PostgreSQL on Render
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```
Add `psycopg2-binary` to `requirements.txt` if you do this.

---

## Part 2: Deploy Frontend to Vercel

1. Push the `frontend/` folder to a GitHub repository (or the same
   monorepo, setting the project root to `frontend/`).
2. In Vercel, click **Add New → Project** and import the repo.
3. Configure:
   - **Framework Preset:** Create React App
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`
4. Add environment variable:
   ```
   REACT_APP_API_BASE_URL=https://<your-service>.onrender.com
   ```
5. Deploy. Your app will be live at `https://<your-project>.vercel.app`.

---

## Part 3: Final Connection Check

1. Update the backend's `ALLOWED_ORIGINS` env var on Render to include
   your final Vercel URL, then redeploy the backend.
2. Open the deployed frontend, go to **Upload & Predict**, and confirm
   a prediction round-trips successfully against the live backend.

---

## Alternative: Docker Deployment

**backend/Dockerfile** (create this if deploying via containers instead):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**frontend/Dockerfile**:
```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Production Checklist

- [ ] Set `DEBUG=False` on the backend
- [ ] Restrict `ALLOWED_ORIGINS` to your actual frontend domain (not `*`)
- [ ] Use a managed database (PostgreSQL) instead of SQLite for durability
- [ ] Use persistent/object storage (e.g. S3, Render Disk) for uploaded images
- [ ] Add HTTPS (both Render and Vercel provide this by default)
- [ ] Set up log monitoring/alerts for the `Full` bin alert path
- [ ] Rate-limit the `/api/predict` endpoint if publicly exposed
