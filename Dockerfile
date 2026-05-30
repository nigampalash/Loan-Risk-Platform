FROM python:3.11-slim

WORKDIR /app/loan-risk-platform

# System deps for mysqlclient build (best-effort)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000 8501

CMD ["python", "backend/app.py"]

