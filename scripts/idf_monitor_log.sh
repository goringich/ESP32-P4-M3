#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$PROJECT_DIR/logs/monitor"

mkdir -p "$LOG_DIR"

STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
LOG_FILE="$LOG_DIR/${STAMP}.log"

if [[ $# -eq 0 ]]; then
  PORT="${ESPPORT:-/dev/ttyUSB0}"
  BAUD="${ESPBAUD:-115200}"
  IDF_ARGS=(-p "$PORT" -b "$BAUD" monitor)
else
  IDF_ARGS=("$@")
fi

CMD=(idf.py "${IDF_ARGS[@]}")
CMD_STR="$(printf '%q ' "${CMD[@]}")"

echo "Logging monitor output to: $LOG_FILE"
echo "Command: ${CMD[*]}"

if command -v script >/dev/null 2>&1; then
  # Keep an interactive TTY for idf_monitor while saving the session log.
  script -q -f -c "$CMD_STR" "$LOG_FILE"
else
  echo "warning: 'script' utility not found, falling back to tee (interactive monitor may be degraded)" >&2
  "${CMD[@]}" 2>&1 | tee "$LOG_FILE"
fi

ln -sfn "$(basename "$LOG_FILE")" "$LOG_DIR/latest.log"
echo "Latest log link: $LOG_DIR/latest.log"
