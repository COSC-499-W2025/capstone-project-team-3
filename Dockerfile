# filepath: /Users/shreyasaxena/Desktop/Capstone/capstone-project-team-3/Dockerfile
# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

# Install system dependencies (git, sqlite3, build tools for NLP)
RUN apt-get update && apt-get install -y \
    git \
    sqlite3 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download Python dependencies with caching
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Download NLP models and data (as root before switching users)
RUN python -m spacy download en_core_web_sm

RUN python -m nltk.downloader punkt_tab cmudict stopwords -d /usr/local/share/nltk_data

# Copy source code and fix ownership
COPY . /app
RUN chown -R appuser:appuser /app

# Switch to non-privileged user
USER appuser

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD ["python", "-m", "app.main"]