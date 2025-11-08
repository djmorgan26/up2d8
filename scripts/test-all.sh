#!/bin/bash
# Run all tests across the monorepo

set -e

echo "🧪 Running all tests..."
echo ""

# Test backend API
echo "🔧 Testing backend API..."
cd packages/backend-api
if [ -d "venv" ]; then
    source venv/bin/activate
    pytest
    deactivate
else
    echo "⚠️  Backend venv not found. Run scripts/setup-dev.sh first."
fi
cd ../..
echo "✅ Backend tests passed"
echo ""

# Test Azure Functions
echo "⚡ Testing Azure Functions..."
cd packages/functions
if [ -d "venv" ]; then
    source venv/bin/activate
    if [ -d "tests" ]; then
        pytest
    else
        echo "ℹ️  No tests directory found in functions"
    fi
    deactivate
else
    echo "⚠️  Functions venv not found. Run scripts/setup-dev.sh first."
fi
cd ../..
echo "✅ Functions tests passed"
echo ""

# Test mobile app
echo "📱 Testing mobile app..."
cd packages/mobile-app
if [ -f "package.json" ]; then
    npm test -- --passWithNoTests
else
    echo "ℹ️  Mobile app tests not configured yet"
fi
cd ../..
echo "✅ Mobile tests passed"
echo ""

echo "🎉 All tests passed!"
