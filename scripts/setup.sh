#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME=${IMAGE_NAME:-capstone-app:latest}
PORT=${PORT:-8000}
PLATFORM=${PLATFORM:-} # e.g. linux/amd64 for Apple Silicon-to-amd64 builds
USE_COMPOSE=${USE_COMPOSE:-0}

function check_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo >&2 "Required: $1 not found"; exit 2; }
}

check_cmd docker

if [ "$USE_COMPOSE" -ne 0 ]; then
  echo "Starting with docker compose..."
  docker compose up --build
  exit 0
fi

echo "Building image: $IMAGE_NAME"
if [ -n "$PLATFORM" ]; then
  docker build --platform="$PLATFORM" -t "$IMAGE_NAME" .
else
  docker build -t "$IMAGE_NAME" .
fi

echo "Running container on port $PORT"
# remove any container with same name
docker rm -f capstone-app-run 2>/dev/null || true
docker run --name capstone-app-run -p "$PORT:8000" --env-file .env -d "$IMAGE_NAME"

echo "Logs: docker logs -f capstone-app-run"