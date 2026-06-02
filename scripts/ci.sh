#!/usr/bin/env bash
# Local CI mirror of Jenkins stages. Run from repository root:
#   ./scripts/ci.sh
# Optional JFrog (jf CLI v2): set JF_URL and JF_ACCESS_TOKEN to run scan/upload.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
VENV="${VENV:-.venv}"

echo "==> Setup Python venv"
"$PYTHON" -m venv "$VENV"
# shellcheck source=/dev/null
source "$VENV/bin/activate"
python -m pip install --upgrade pip
pip install -e ".[dev]"

echo "==> Static analysis"
./scripts/analyse.sh

echo "==> Test"
pytest -v --cov=hello_world --cov-report=term --cov-report=xml

echo "==> Build"
python -m build
python -m hello_world --version 2>/dev/null || hello-world --version

VERSION="$(python -c "from hello_world import __version__; print(__version__)")"
echo "Package version: ${VERSION}"

if command -v jf >/dev/null 2>&1 && [[ -n "${JF_URL:-}" ]] && [[ -n "${JF_ACCESS_TOKEN:-}" ]]; then
  echo "==> Xray scan (jf)"
  export JFROG_CLI_LOG_LEVEL="${JFROG_CLI_LOG_LEVEL:-ERROR}"
  jf scan dist/ --fail

  if [[ "${CI_PUBLISH:-false}" == "true" ]]; then
  REPO="${JF_RT_REPO:-pypi-local}"
  TARGET="${REPO}/hello-world/${VERSION}/"
  echo "==> Upload to Artifactory (${TARGET})"
  jf rt upload "dist/*" "${TARGET}" \
    --build-name=hello-world \
    --build-number="${BUILD_NUMBER:-local}"
  fi
else
  echo "Skipping jf scan/upload (set JF_URL + JF_ACCESS_TOKEN, install jf CLI to enable)"
fi

echo "==> Done"
