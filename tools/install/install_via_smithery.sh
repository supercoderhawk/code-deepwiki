#!/usr/bin/env bash
set -euo pipefail

SKILL=""
AGENT=""
GLOBAL=0

usage() {
  cat <<'USAGE'
Install a skill via Smithery CLI.

Usage:
  install_via_smithery.sh --skill <namespace/slug|url> [options]

Options:
  --skill <identifier>     Required. Smithery namespace/slug or skill URL
  --agent <name>           Optional target agent (e.g. claude-code, github-copilot)
  --global                 Install globally (user-level)
  -h, --help               Show this help

Examples:
  bash tools/install/install_via_smithery.sh --skill namespace/skill-name --agent claude-code
  bash tools/install/install_via_smithery.sh --skill https://smithery.ai/skills/namespace/skill-name --agent github-copilot
  bash tools/install/install_via_smithery.sh --skill namespace/skill-name --agent claude-code --global
USAGE
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
