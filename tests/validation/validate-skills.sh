#!/bin/bash
# Repository validation entrypoint

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

FAILED=0

run_check() {
    local label=$1
    shift

    echo "Checking ${label}..."
    if "$@"; then
        echo -e "${GREEN}✓${NC} ${label}"
    else
        echo -e "${RED}✗${NC} ${label}"
        FAILED=1
    fi
    echo
}

echo "======================================"
echo "Rust Skills Validation"
echo "======================================"
echo

run_check "repository integrity" python3 "$ROOT_DIR/scripts/validate_repo.py"
run_check "hook matcher tests" python3 "$ROOT_DIR/tests/hook-matcher-test.py"
run_check "trigger script self-check" bash "$ROOT_DIR/test-triggers.sh" --self-check

echo "======================================"
if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
else
    echo -e "${RED}Some checks failed.${NC}"
fi
echo "======================================"

exit "$FAILED"
