#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  cat <<'EOF'
Install skills from this repository into an AI agent skills directory.

Usage:
  scripts/install-skills.sh --agent <codex|claude|custom> [options]

Options:
  --agent <name>       Target agent: codex, claude, or custom (required)
  --scope <user|repo>  Install scope (default: user)
  --skill <name>       Install a single skill directory (repeatable)
  --all                Install all skills found at repo root
  --target <path>      Override target skills directory
  --force              Overwrite destination skill directories
  --dry-run            Print planned actions without copying files
  -h, --help           Show this help

Examples:
  scripts/install-skills.sh --agent codex --all
  scripts/install-skills.sh --agent claude --skill product-minded-dev
  scripts/install-skills.sh --agent custom --target ~/.my-agent/skills --all
EOF
}

AGENT=""
SCOPE="user"
TARGET_DIR=""
FORCE=0
DRY_RUN=0
INSTALL_ALL=0
SKILLS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      AGENT="${2:-}"
      shift 2
      ;;
    --scope)
      SCOPE="${2:-}"
      shift 2
      ;;
    --skill)
      SKILLS+=("${2:-}")
      shift 2
      ;;
    --all)
      INSTALL_ALL=1
      shift
      ;;
    --target)
      TARGET_DIR="${2:-}"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "${AGENT}" ]]; then
  echo "--agent is required" >&2
  usage
  exit 1
fi

if [[ "${SCOPE}" != "user" && "${SCOPE}" != "repo" ]]; then
  echo "--scope must be one of: user, repo" >&2
  exit 1
fi

resolve_target() {
  if [[ -n "${TARGET_DIR}" ]]; then
    printf '%s\n' "${TARGET_DIR}"
    return
  fi

  case "${AGENT}" in
    codex)
      if [[ "${SCOPE}" == "repo" ]]; then
        printf '%s\n' "${REPO_ROOT}/.codex/skills"
      else
        if [[ -n "${CODEX_HOME:-}" ]]; then
          printf '%s\n' "${CODEX_HOME}/skills"
        else
          printf '%s\n' "${HOME}/.codex/skills"
        fi
      fi
      ;;
    claude)
      if [[ "${SCOPE}" == "repo" ]]; then
        printf '%s\n' "${REPO_ROOT}/.claude/skills"
      else
        printf '%s\n' "${HOME}/.claude/skills"
      fi
      ;;
    custom)
      echo "custom agent requires --target <path>" >&2
      exit 1
      ;;
    *)
      echo "Unsupported --agent '${AGENT}'. Use codex, claude, or custom." >&2
      exit 1
      ;;
  esac
}

discover_skills() {
  local path
  while IFS= read -r path; do
    dirname "${path}" | sed "s#^${REPO_ROOT}/##"
  done < <(find "${REPO_ROOT}" -mindepth 2 -maxdepth 2 -type f -name "SKILL.md" | sort)
}

DEST="$(resolve_target)"

if [[ ${INSTALL_ALL} -eq 1 ]]; then
  SKILLS=()
  while IFS= read -r skill_path; do
    SKILLS+=("${skill_path}")
  done < <(discover_skills)
fi

if [[ ${#SKILLS[@]} -eq 0 ]]; then
  echo "No skills selected. Pass --all or one or more --skill <name>." >&2
  exit 1
fi

copy_skill() {
  local skill_name="$1"
  local src="${REPO_ROOT}/${skill_name}"
  local dst="${DEST}/${skill_name}"

  if [[ ! -f "${src}/SKILL.md" ]]; then
    echo "Skipping '${skill_name}': missing ${src}/SKILL.md" >&2
    return 1
  fi

  if [[ -d "${dst}" && ${FORCE} -ne 1 ]]; then
    echo "Skipping '${skill_name}': destination exists (${dst}). Use --force to overwrite."
    return 0
  fi

  echo "Installing ${skill_name} -> ${dst}"
  if [[ ${DRY_RUN} -eq 1 ]]; then
    return 0
  fi

  mkdir -p "${DEST}"
  rm -rf "${dst}"
  cp -R "${src}" "${dst}"
}

echo "Agent      : ${AGENT}"
echo "Scope      : ${SCOPE}"
echo "Repository : ${REPO_ROOT}"
echo "Target     : ${DEST}"
echo "Dry run    : ${DRY_RUN}"
echo

status=0
for skill in "${SKILLS[@]}"; do
  if ! copy_skill "${skill}"; then
    status=1
  fi
done

exit "${status}"
