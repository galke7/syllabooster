# ---------- Builder: create the SQLite DB inside the image ----------
FROM python:3.11-slim AS builder

# System deps for sqlite and building wheels (many Python libs on slim don't need build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 tzdata ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only what we need to build the DB
COPY schema.sql seed.sql ./

# Build app.db from schema + seed
RUN sqlite3 /app.db < /app/schema.sql && \
    sqlite3 /app.db < /app/seed.sql

# ---------- Final runtime image ----------
FROM python:3.11-slim

# System deps for runtime only (sqlite3 CLI not strictly required at runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata ca-certificates \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    DB_PATH=/app.db

WORKDIR /app

# Copy code and static/templates
COPY . .

# Get the DB and installed site-packages from builder
COPY --from=builder /app.db /app.db
# Install deps again in final image (smaller than copying site-packages)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# (Optional) drop root
RUN useradd -m -u 10001 appuser
USER appuser

EXPOSE 8080

# IMPORTANT: gunicorn must point to <module>:<wsgi_app>
# If your file isn't app.py or the app object isn't "app", change this.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "app:app"]