#!/usr/bin/env bash
set -euo pipefail

SOURCE="supercoderhawk/code-deepwiki"
SKILL="code-deepwiki"
FIND_QUERY="code-deepwiki"
NO_FIND=0
YES=1
AGENTS=()

usage() {
  cat <<'USAGE'
Trigger skills.sh discovery for this repository via npx skills.

Important:
  skills.sh does not provide a separate "publish" command.
  Discovery/ranking is driven by anonymous install telemetry from `skills add`.

Usage:
  push_to_skills_sh.sh [options]

Options:
  --source <owner/repo|url>  Remote source to install from (default: supercoderhawk/code-deepwiki)
  --skill <name>             Skill name to install (default: code-deepwiki)
  --agent <name>             Target agent; may be repeated (e.g. codex, claude-code)
  --find-query <text>        Query used for post-check (default: code-deepwiki)
  --no-find                  Skip post-check using `skills find`
  --yes                      Add --yes for non-interactive install (default: enabled)
  --no-yes                   Disable --yes
  -h, --help                 Show this help

Examples:
  bash tools/publish/push_to_skills_sh.sh
  bash tools/publish/push_to_skills_sh.sh --agent codex
  bash tools/publish/push_to_skills_sh.sh --source supercoderhawk/code-deepwiki --agent codex --agent claude-code
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)
      [[ $# -ge 2 ]] || { echo "[ERROR] --source requires a value" >&2; exit 1; }
      SOURCE="$2"
      shift 2
      ;;
    --skill)
      [[ $# -ge 2 ]] || { echo "[ERROR] --skill requires a value" >&2; exit 1; }
      SKILL="$2"
      shift 2
      ;;
    --agent)
      [[ $# -ge 2 ]] || { echo "[ERROR] --agent requires a value" >&2; exit 1; }
      AGENTS+=("$2")
      shift 2
      ;;
    --find-query)
      [[ $# -ge 2 ]] || { echo "[ERROR] --find-query requires a value" >&2; exit 1; }
      FIND_QUERY="$2"
      shift 2
      ;;
    --no-find)
      NO_FIND=1
      shift
      ;;
    --yes)
      YES=1
      shift
      ;;
    --no-yes)
      YES=0
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

CMD=(npx -y skills add "$SOURCE" --skill "$SKILL")
for agent in "${AGENTS[@]}"; do
  CMD+=(--agent "$agent")
done
if [[ "$YES" -eq 1 ]]; then
  CMD+=(--yes)
fi

printf 'Running:'
for arg in "${CMD[@]}"; do
  printf ' %q' "$arg"
done
printf '\n'

"${CMD[@]}"

if [[ "$NO_FIND" -eq 0 ]]; then
  FIND_CMD=(npx -y skills find "$FIND_QUERY")
  printf 'Running:'
  for arg in "${FIND_CMD[@]}"; do
    printf ' %q' "$arg"
  done
  printf '\n'
  "${FIND_CMD[@]}"
fi
