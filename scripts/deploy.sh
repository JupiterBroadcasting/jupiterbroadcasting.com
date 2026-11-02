#!/bin/bash
set -euo pipefail

# Contract: args passed from GitHub Action runner via 'bash -s' environment
# Fallback to positional parameters for flexibility
PROJECT_PATH="${PROJECT_PATH:-$1}"
GH_ACTOR="${GH_ACTOR:-$2}"
GH_TOKEN="${GH_TOKEN:-$3}"

echo "===> Entering project directory: $PROJECT_PATH"
cd "$PROJECT_PATH"

echo "===> Logging into GitHub Container Registry..."
echo "$GH_TOKEN" | docker login ghcr.io -u "$GH_ACTOR" --password-stdin

echo "===> Updating source code (fetch + hard reset)..."
git fetch origin main
git reset --hard origin/main

echo "===> Building production Docker image..."
docker build --no-cache -t ghcr.io/jupiterbroadcasting/jupiterbroadcasting.com:latest .

echo "===> Pushing image to registry..."
docker push ghcr.io/jupiterbroadcasting/jupiterbroadcasting.com:latest

echo "===> Cleaning up Docker system (pruning)..."
docker container prune -f
docker image prune -f
docker builder prune -f

echo "===> Restarting services with Docker Compose..."
docker compose -f ~/docker-compose.yml up -d jb-jbcom

echo "===> Deployment successful!"
