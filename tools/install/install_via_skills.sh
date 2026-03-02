#!/usr/bin/env bash
set -euo pipefail

SOURCE="."
GLOBAL=0
YES=0
AGENTS=()

usage() {
  cat <<'USAGE'
Install code-deepwiki via Vercel Skills CLI.

Usage:
  install_via_skills.sh [options]

Options:
  --source <path-or-url>   Skill source path or repository URL (default: .)
  --agent <name>           Target agent; may be repeated
  --global                 Install globally (user-level)
  --yes                    Skip prompts
  -h, --help               Show this help

Examples:
  bash tools/install/install_via_skills.sh --source .
  bash tools/install/install_via_skills.sh --source supercoderhawk/code-deepwiki --agent codex --yes
  bash tools/install/install_via_skills.sh --source . --agent claude-code --yes
  bash tools/install/install_via_skills.sh --source . --agent github-copilot --global --yes
  bash tools/install/install_via_skills.sh --source https://github.com/supercoderhawk/code-deepwiki --agent claude-code
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      [[ $# -ge 2 ]] || { echo "[ERROR] --source requires a value" >&2; exit 1; }
      SOURCE="$2"
      shift 2
      ;;
    --agent)
      [[ $# -ge 2 ]] || { echo "[ERROR] --agent requires a value" >&2; exit 1; }
      AGENTS+=("$2")
      shift 2
      ;;
    --global)
      GLOBAL=1
      shift
      ;;
    --yes)
      YES=1
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

CMD=(npx -y skills add "$SOURCE" --skill code-deepwiki)
for agent in "${AGENTS[@]}"; do
  CMD+=(--agent "$agent")
done
if [[ "$GLOBAL" -eq 1 ]]; then
  CMD+=(--global)
fi
if [[ "$YES" -eq 1 ]]; then
  CMD+=(--yes)
fi

printf 'Running:'
for arg in "${CMD[@]}"; do
  printf ' %q' "$arg"
done
printf '\n'

"${CMD[@]}"
