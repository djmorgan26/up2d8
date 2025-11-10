#!/bin/bash
# Production Test Runner for UP2D8
# Usage: ./scripts/run_production_tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
TEST_MODE="${PROD_TEST_MODE:-mock}"
REPORT_DIR="test-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --live)
            TEST_MODE="live"
            shift
            ;;
        --mock)
            TEST_MODE="mock"
            shift
            ;;
        --critical-only)
            CRITICAL_ONLY=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --live           Run tests against production (default: mock)"
            echo "  --mock           Run tests in mock mode (default)"
            echo "  --critical-only  Run only critical tests"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Create report directory
mkdir -p "$REPORT_DIR"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}UP2D8 Production Test Suite${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo "Test Mode: $TEST_MODE"
echo "Timestamp: $TIMESTAMP"
echo "Report Dir: $REPORT_DIR"
echo ""

# Check if running in live mode
if [ "$TEST_MODE" = "live" ]; then
    echo -e "${RED}WARNING: Running tests against PRODUCTION${NC}"
    echo "This will make real requests to production services."
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Set environment variable
export PROD_TEST_MODE=$TEST_MODE

# Build pytest command
PYTEST_CMD="pytest tests/production/"
PYTEST_ARGS="-v --tb=short --html=$REPORT_DIR/report_${TIMESTAMP}.html --self-contained-html"

# Add critical-only filter if specified
if [ "$CRITICAL_ONLY" = true ]; then
    PYTEST_ARGS="$PYTEST_ARGS -m critical"
fi

# Run tests
echo -e "${GREEN}Running tests...${NC}"
echo ""

if $PYTEST_CMD $PYTEST_ARGS; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}All tests passed!${NC}"
    echo -e "${GREEN}========================================${NC}"
    EXIT_CODE=0
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Some tests failed!${NC}"
    echo -e "${RED}========================================${NC}"
    EXIT_CODE=1
fi

echo ""
echo "Report saved to: $REPORT_DIR/report_${TIMESTAMP}.html"

exit $EXIT_CODE
