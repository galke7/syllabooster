# ---------- Builder: create the SQLite DB inside the image ----------
FROM python:3.11-slim AS builder

# System deps for sqlite and building wheels (many Python libs on slim don't need build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 tzdata ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# ---------- Builder ----------
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY schema.sql seed.sql ./
# Build DB under /app
RUN sqlite3 /app/app.db < /app/schema.sql && \
    sqlite3 /app/app.db < /app/seed.sql && \
    sqlite3 /app/app.db "PRAGMA journal_mode=DELETE;"    # avoid WAL files on read-only FS

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
COPY . .
COPY --from=builder /app/app.db /app/app.db
RUN chmod 0644 /app/app.db
ENV PORT=8080 \
    DB_PATH=/app/app.db
    
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