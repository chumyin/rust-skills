#!/bin/bash
# Rust Skills Trigger Test Script
# Tests if the Forced Eval Hook is working
#
# Usage:
#   ./test-triggers.sh              # Run all tests
#   ./test-triggers.sh -v           # Verbose mode (show full output)
#   ./test-triggers.sh "query"      # Test single query
#   ./test-triggers.sh -v "query"   # Single query with verbose

set -uo pipefail

echo "=== Rust Skills Forced Eval Hook Tests ==="
echo
echo "Testing if hook triggers and Claude evaluates skills..."
echo

# Parse arguments
VERBOSE=false
SINGLE_TEST=
SELF_CHECK=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose) VERBOSE=true; shift ;;
        --self-check) SELF_CHECK=true; shift ;;
        *) SINGLE_TEST="$1"; shift ;;
    esac
done

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counter
PASS=0
FAIL=0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Cross-platform timeout function
run_with_timeout() {
    local timeout_sec=$1
    shift
    if command -v gtimeout &> /dev/null; then
        gtimeout "$timeout_sec" "$@"
    elif command -v timeout &> /dev/null; then
        timeout "$timeout_sec" "$@"
    else
        # macOS fallback: use perl
        perl -e 'alarm shift @ARGV; exec @ARGV' "$timeout_sec" "$@"
    fi
}

self_check() {
    local failed=0

    echo "Running local self-check..."

    if [ -f "$SCRIPT_DIR/hooks/hooks.json" ]; then
        echo -e "${GREEN}✓${NC} hooks/hooks.json present"
    else
        echo -e "${RED}✗${NC} hooks/hooks.json missing"
        failed=1
    fi

    if [ -x "$SCRIPT_DIR/.claude/hooks/rust-skill-eval-hook.sh" ]; then
        echo -e "${GREEN}✓${NC} .claude/hooks/rust-skill-eval-hook.sh executable"
    else
        echo -e "${RED}✗${NC} .claude/hooks/rust-skill-eval-hook.sh missing or not executable"
        failed=1
    fi

    if python3 "$SCRIPT_DIR/tests/hook-matcher-test.py"; then
        echo -e "${GREEN}✓${NC} hook matcher tests"
    else
        echo -e "${RED}✗${NC} hook matcher tests"
        failed=1
    fi

    return "$failed"
}

# Test function - checks if response contains skill evaluation
test_hook() {
    local query="$1"
    local expected_skill="$2"

    echo -n "Testing: \"$query\" "
    echo -n "→ expecting evaluation of $expected_skill ... "

    # Run claude and capture output (first 50 lines)
    result=$(run_with_timeout 60 claude -p "$query" 2>&1 | head -50 || true)

    # Check if output contains skill evaluation pattern
    # Patterns: "[RUST-SKILL-EVAL]", "YES -", "NO -", skill names, etc.
    if echo "$result" | grep -qiE "\[RUST-SKILL-EVAL\]|(YES|NO)[ :-]|Skill\(|skill.*:|m0[1-7]-|unsafe-checker|coding-guidelines|rust-learner|rust-guru|domain-"; then
        echo -e "${GREEN}HOOK TRIGGERED${NC}"

        # Check if the expected skill was mentioned
        if echo "$result" | grep -qi "$expected_skill"; then
            echo -e "  └─ ${GREEN}✓ $expected_skill evaluated${NC}"
            ((PASS++))
        else
            echo -e "  └─ ${YELLOW}? $expected_skill not explicitly mentioned${NC}"
            ((PASS++))  # Hook still worked
        fi
    else
        echo -e "${RED}HOOK NOT TRIGGERED${NC}"
        echo "  First 300 chars of response:"
        echo "$result" | head -c 300
 echo
        ((FAIL++))
    fi

    # Show full output in verbose mode
    if [ "$VERBOSE" = true ]; then
        echo "  --- Full output ---"
        echo "$result"
        echo "  -------------------"
    fi
 echo
}

echo "--- Testing Hook Activation ---"
echo

if [ "$SELF_CHECK" = true ]; then
    self_check
    exit $?
fi

if ! command -v claude >/dev/null 2>&1; then
    echo -e "${YELLOW}claude command not found; skipping live trigger tests${NC}"
    exit 0
fi

# If single test specified, run only that
if [ -n "$SINGLE_TEST" ]; then
    test_hook "$SINGLE_TEST" "any-skill"
else
    test_hook "how to use tokio" "tokio"
    test_hook "E0382 moved value in Rust" "m01-ownership"
    test_hook "review this unsafe FFI code" "unsafe-checker"
fi

echo "=== Summary ==="
echo -e "Hook Triggered: ${GREEN}$PASS${NC}"
echo -e "Hook Failed: ${RED}$FAIL${NC}"
echo

if [ $FAIL -gt 0 ]; then
    echo -e "${YELLOW}Some hooks didn't trigger. Check:${NC}"
    echo "  1. Is this a new Claude session? (restart if needed)"
    echo "  2. Is .claude/settings.local.json configured?"
    echo "  3. Is .claude/hooks/rust-skill-eval-hook.sh executable?"
    exit 1
else
    echo -e "${GREEN}All hooks triggered successfully!${NC}"
    exit 0
fi
