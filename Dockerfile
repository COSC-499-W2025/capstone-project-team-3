# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

# Install git and sqlite3
RUN apt-get update && apt-get install -y \
    git \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        texlive-latex-base \
        texlive-latex-extra \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        latexmk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set NLTK data directory (BEFORE creating user)
ENV NLTK_DATA=/usr/local/share/nltk_data

# Set HuggingFace cache directory
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface/transformers
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers

# Suppress noisy warnings globally in container
ENV PYTHONWARNINGS="ignore::DeprecationWarning,ignore::FutureWarning,ignore:Using `TRANSFORMERS_CACHE` is deprecated:FutureWarning,ignore:All support for the `google.generativeai` package has ended:FutureWarning","ignore:pkg_resources is deprecated as an API:UserWarning"

WORKDIR /app

# Create cache directories
RUN mkdir -p /app/.cache/huggingface/transformers /app/.cache/sentence-transformers

# Create non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install Python dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Download NLP models BEFORE switching users
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader punkt_tab punkt cmudict stopwords -d /usr/local/share/nltk_data

# Pre-download sentence-transformers model as root
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy source code
COPY . /app

# Fix ownership (including cache directories)
RUN chown -R appuser:appuser /app

# Switch to non-privileged user
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "app.main"]