#!/usr/bin/env bash
set -euo pipefail

SKILL=""
AGENT=""
GLOBAL=0
AUTH_FILE="auth.json"

usage() {
  cat <<'USAGE'
Install a skill via Smithery CLI.

Usage:
  install_via_smithery.sh --skill <supercoderhawk/code-deepwiki|url> [options]

Options:
  --skill <identifier>     Required. Smithery skill ID or URL (e.g. supercoderhawk/code-deepwiki)
  --agent <name>           Optional target agent (e.g. claude-code, github-copilot)
  --global                 Install globally (user-level)
  --auth-file <path>       Auth JSON file path (default: auth.json)
  -h, --help               Show this help

Examples:
  bash tools/install/install_via_smithery.sh --skill supercoderhawk/code-deepwiki --agent claude-code
  bash tools/install/install_via_smithery.sh --skill https://smithery.ai/skills/supercoderhawk/code-deepwiki --agent github-copilot
  bash tools/install/install_via_smithery.sh --skill supercoderhawk/code-deepwiki --agent claude-code --global
  bash tools/install/install_via_smithery.sh --skill supercoderhawk/code-deepwiki --auth-file ./auth.json
USAGE
}

get_auth_value() {
  local file="$1"
  local key="$2"
  python3 - "$file" "$key" <<'PY'
import json
import pathlib
import sys

auth_path = pathlib.Path(sys.argv[1]).expanduser()
key = sys.argv[2]
if not auth_path.exists():
    print("")
    raise SystemExit(0)

try:
    data = json.loads(auth_path.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"[ERROR] Failed to read auth JSON: {auth_path} ({exc})", file=sys.stderr)
    raise SystemExit(1)

if not isinstance(data, dict):
    print(f"[ERROR] Auth JSON must be an object: {auth_path}", file=sys.stderr)
    raise SystemExit(1)

value = data.get(key, "")
if isinstance(value, str):
    print(value.strip())
else:
    print("")
PY
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skill)
      [[ $# -ge 2 ]] || { echo "[ERROR] --skill requires a value" >&2; exit 1; }
      SKILL="$2"
      shift 2
      ;;
    --agent)
      [[ $# -ge 2 ]] || { echo "[ERROR] --agent requires a value" >&2; exit 1; }
      AGENT="$2"
      shift 2
      ;;
    --global)
      GLOBAL=1
      shift
      ;;
    --auth-file)
      [[ $# -ge 2 ]] || { echo "[ERROR] --auth-file requires a value" >&2; exit 1; }
      AUTH_FILE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[ERROR] Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$SKILL" ]]; then
  echo "[ERROR] --skill is required" >&2
  usage
  exit 1
fi

if [[ -z "${SMITHERY_API_KEY:-}" ]]; then
  auth_key="$(get_auth_value "$AUTH_FILE" "SMITHERY_API_KEY")"
  if [[ -n "$auth_key" ]]; then
    export SMITHERY_API_KEY="$auth_key"
    echo "[INFO] Loaded SMITHERY_API_KEY from $AUTH_FILE"
  fi
fi

CMD=(npx -y @smithery/cli skill add "$SKILL")
if [[ -n "$AGENT" ]]; then
  CMD+=(--agent "$AGENT")
fi
if [[ "$GLOBAL" -eq 1 ]]; then
  CMD+=(--global)
fi

printf 'Running:'
for arg in "${CMD[@]}"; do
  printf ' %q' "$arg"
done
printf '\n'

"${CMD[@]}"
