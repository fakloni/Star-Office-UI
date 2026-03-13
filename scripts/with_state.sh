#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [[ $# -lt 4 ]]; then
  echo "Usage: $0 <state> <detail> -- <command...>"
  exit 1
fi

STATE="$1"
DETAIL="$2"
shift 2

if [[ "$1" != "--" ]]; then
  echo "Usage: $0 <state> <detail> -- <command...>"
  exit 1
fi
shift

cd "$ROOT_DIR"
python3 set_state.py "$STATE" "$DETAIL"

cleanup() {
  cd "$ROOT_DIR"
  python3 set_state.py idle "待命中" >/dev/null 2>&1 || true
}
trap cleanup EXIT

"$@"
