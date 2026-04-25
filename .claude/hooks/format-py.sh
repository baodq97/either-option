#!/usr/bin/env bash
# PostToolUse hook: auto-format a single .py file after Write/Edit.
# Stdin: tool-call JSON. Reads .tool_response.filePath or .tool_input.file_path.
# Exit 0 always (best-effort; Stop hook is authoritative).

set -uo pipefail

f=$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')
[[ -z "$f" ]] && exit 0
[[ "$f" != *.py ]] && exit 0

# --force-exclude so reference/ stays untouched even with explicit file path.
uv run --quiet ruff check --fix --force-exclude --quiet -- "$f" >/dev/null 2>&1 || true
uv run --quiet ruff format --force-exclude --quiet -- "$f" >/dev/null 2>&1 || true
exit 0
