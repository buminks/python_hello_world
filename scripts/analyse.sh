#!/usr/bin/env bash
# Run static analysis tools; write *.log and *.exit in the current directory.
# Usage: ./scripts/analyse.sh [tool ...]   (default: all)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VENV="${VENV:-.venv}"
if [[ ! -f "${VENV}/bin/activate" ]]; then
  echo "Virtualenv not found at ${VENV}; run setup first." >&2
  exit 1
fi
# shellcheck source=/dev/null
source "${VENV}/bin/activate"

run_tool() {
  local name="$1"
  shift
  echo "==> ${name}"
  set +e
  "$@" > "${name}.log" 2>&1
  echo $? > "${name}.exit"
  set -e
  cat "${name}.exit"
}

run_isort() {
  run_tool isort isort --check-only --diff src tests
}

run_flake8() {
  run_tool flake8 flake8 src tests
}

run_pylint() {
  run_tool pylint pylint --output-format=parseable src/hello_world tests
}

run_ruff() {
  run_tool ruff ruff check src tests
}

run_mypy() {
  run_tool mypy mypy src/hello_world
}

run_bandit() {
  run_tool bandit bandit -r src/hello_world -f txt
}

ALL=(isort flake8 pylint ruff mypy bandit)

if [[ $# -eq 0 ]]; then
  TOOLS=("${ALL[@]}")
else
  TOOLS=("$@")
fi

for tool in "${TOOLS[@]}"; do
  case "${tool}" in
    isort) run_isort ;;
    flake8) run_flake8 ;;
    pylint) run_pylint ;;
    ruff) run_ruff ;;
    mypy) run_mypy ;;
    bandit) run_bandit ;;
    *)
      echo "Unknown tool: ${tool}" >&2
      exit 2
      ;;
  esac
done

failed=0
for tool in "${TOOLS[@]}"; do
  code=$(cat "${tool}.exit")
  if [[ "${code}" -ne 0 ]]; then
    echo "${tool} failed (exit ${code})"
    failed=1
  fi
done
exit "${failed}"
