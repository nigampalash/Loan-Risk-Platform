# Stage 1: Build React Frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --legacy-peer-deps
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Python Backend & Package Frontend
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies (best effort for scientific modules)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code and models
COPY backend/ ./backend/
COPY models/ ./models/
COPY datasets/ ./datasets/
COPY train_model.py predict.py ./

# Create directories for persistent assets
RUN mkdir -p saved_models reports

# Copy static frontend build from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 5000

ENV PORT=5000
ENV MODEL_DIR=saved_models
ENV REPORTS_DIR=reports

# Run FastAPI app
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "5000"]
