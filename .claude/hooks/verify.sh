#!/usr/bin/env bash
# Stop hook (asyncRewake): runs the 4-check verify loop in background.
# Exit 0 = silent success. Exit 2 = wake Claude with the failures.

set -uo pipefail

fail=0
buf=""

check() {
    local label="$1"
    shift
    local out
    if ! out=$("$@" 2>&1); then
        fail=1
        buf+="=== ${label} FAILED ==="$'\n'"${out}"$'\n\n'
    fi
}

check "ruff format --check" uv run --quiet ruff format --check .
check "ruff check"          uv run --quiet ruff check .
check "pyright"             uv run --quiet pyright
check "pytest"              uv run --quiet pytest -q

if [ "${fail}" -ne 0 ]; then
    echo "Verify loop failed before stop. Fix and re-verify before declaring done:"
    echo
    printf '%s' "${buf}"
    exit 2
fi
exit 0
