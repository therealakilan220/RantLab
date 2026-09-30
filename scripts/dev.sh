#!/usr/bin/env bash
# Start backend (port 8000) and frontend (port 3000) together. Ctrl+C stops both.
# Activate the Python virtual environment first (see README).
set -e
cd "$(dirname "$0")/.."

(cd backend && uvicorn app.main:app --reload --port 8000) &
BACKEND_PID=$!
trap 'kill $BACKEND_PID 2>/dev/null' EXIT

cd frontend && npm run dev
