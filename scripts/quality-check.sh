#!/bin/bash
# Quality checks for rust-skills

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

FAILED=0

run_check() {
    local label=$1
    shift

    echo "Checking ${label}..."
    if "$@"; then
        echo -e "${GREEN}OK:${NC} ${label}"
    else
        echo -e "${RED}ERROR:${NC} ${label}"
        FAILED=1
    fi
    echo
}

echo "======================================"
echo "Rust Skills Quality Check"
echo "======================================"
echo

run_check "python syntax" \
    python3 -m py_compile \
    "$ROOT_DIR/scripts/repo_manifest.py" \
    "$ROOT_DIR/scripts/render_repository_artifacts.py" \
    "$ROOT_DIR/scripts/validate_repo.py" \
    "$ROOT_DIR/tests/hook-matcher-test.py"

run_check "shell syntax" \
    bash -n \
    "$ROOT_DIR/test-triggers.sh" \
    "$ROOT_DIR/tests/validation/validate-skills.sh" \
    "$ROOT_DIR/scripts/quality-check.sh"

run_check "repository validation" python3 "$ROOT_DIR/scripts/validate_repo.py"
run_check "hook matcher tests" python3 "$ROOT_DIR/tests/hook-matcher-test.py"
run_check "trigger script self-check" bash "$ROOT_DIR/test-triggers.sh" --self-check

echo "======================================"
if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}Quality check PASSED${NC}"
else
    echo -e "${RED}Quality check FAILED${NC}"
fi

exit "$FAILED"
