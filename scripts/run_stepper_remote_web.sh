#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${REPO_DIR}/stepper-remote/frontend"
BACKEND_DIR="${REPO_DIR}/stepper-remote/backend"
HOST="${STEPPER_REMOTE_HOST:-127.0.0.1}"
PORT="${STEPPER_REMOTE_PORT:-3001}"

is_loopback() {
  [[ "$1" == "127.0.0.1" || "$1" == "localhost" || "$1" == "::1" || "$1" == "[::1]" ]]
}

if ! is_loopback "${HOST}" && [[ "${STEPPER_REMOTE_ALLOW_REMOTE:-0}" != "1" ]]; then
  echo "[stepper-remote] refusing remote bind to ${HOST}" >&2
  echo "[stepper-remote] set STEPPER_REMOTE_ALLOW_REMOTE=1 explicitly if LAN access is intended" >&2
  exit 2
fi

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

echo "[stepper-remote] starting backend on http://${HOST}:${PORT}"
if ! is_loopback "${HOST}"; then
  echo "[stepper-remote] WARNING: remote operator access can build, flash, and control hardware"
  echo "[stepper-remote] restrict the host firewall and set STEPPER_REMOTE_ALLOWED_ORIGIN"
fi

exec bash -lc "cd '${BACKEND_DIR}' && npm start"
