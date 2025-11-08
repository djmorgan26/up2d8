#!/bin/bash
# UP2D8 Development Environment Setup

set -e

echo "🏗️  Setting up UP2D8 monorepo development environment..."
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Please install Node.js >= 18."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Please install Python >= 3.10."; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "❌ pip is required but not installed."; exit 1; }

echo "✅ Prerequisites met"
echo ""

# Install mobile app dependencies
echo "📱 Installing mobile app dependencies..."
cd packages/mobile-app
npm install
cd ../..
echo "✅ Mobile app dependencies installed"
echo ""

# Set up Python virtual environments for backend
echo "🐍 Setting up backend API virtual environment..."
cd packages/backend-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ../..
echo "✅ Backend API environment ready"
echo ""

# Set up Python virtual environment for functions
echo "⚡ Setting up Azure Functions virtual environment..."
cd packages/functions
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ../..
echo "✅ Azure Functions environment ready"
echo ""

echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure your environment variables"
echo "2. Start backend: npm run backend:dev"
echo "3. Start mobile app: npm run mobile:ios (or mobile:android)"
echo "4. Run tests: npm run test:all"
echo ""
