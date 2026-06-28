#!/usr/bin/env bash
# Local validation suite orchestrator for the NudgeWhen v0.1.0 release.
# Thin shell wrapper around the Python standard-library validator.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VALIDATOR="${SCRIPT_DIR}/validate_local.py"

if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' "FAIL prerequisite/python — python3 not found on PATH" >&2
    exit 2
fi

if ! python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' \
    >/dev/null 2>&1
then
    printf '%s\n' "FAIL prerequisite/python — Python 3.10 or newer is required" >&2
    exit 2
fi

if [ ! -f "${VALIDATOR}" ]; then
    printf '%s\n' "FAIL prerequisite/validator — validator script not found" >&2
    exit 2
fi

cd "${REPO_ROOT}"
export PYTHONDONTWRITEBYTECODE=1
exec python3 "${VALIDATOR}" "$@"
