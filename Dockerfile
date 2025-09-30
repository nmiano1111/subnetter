# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false

# System deps (psycopg2 build not needed; you're using asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Only copy metadata first to leverage Docker layer cache
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root

# Now copy the actual app
COPY app ./app

# (Optional) if you have a package at repo root, uncomment:
# RUN poetry install --only main

EXPOSE 8000

# Use a non-root user
RUN useradd -m appuser
USER appuser

# Start FastAPI (uvicorn). Your app’s startup will run create_all().
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
