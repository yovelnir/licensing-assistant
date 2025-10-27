# backend/Dockerfile
FROM python:3.12-slim

# System basics (faster builds, better wheels)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build tooling in case any wheel compiles
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Railway provides $PORT; Gunicorn should bind to it
CMD ["sh", "-c", "gunicorn -w 2 -k gthread -b 0.0.0.0:$PORT wsgi:app"]