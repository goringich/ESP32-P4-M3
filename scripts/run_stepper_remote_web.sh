#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${REPO_DIR}/stepper-remote/frontend"
BACKEND_DIR="${REPO_DIR}/stepper-remote/backend"

echo "[stepper-remote] building frontend"
(
  cd "${FRONTEND_DIR}"
  npm run build
)

echo "[stepper-remote] building backend"
(
  cd "${BACKEND_DIR}"
  npm run build
)

echo "[stepper-remote] starting backend on http://127.0.0.1:3001"
echo "[stepper-remote] open http://127.0.0.1:3001/ in a browser"
exec bash -lc "cd '${BACKEND_DIR}' && npm start"
