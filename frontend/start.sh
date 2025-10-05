#!/bin/bash

# PlayCricket Frontend Quick Start Script

set -e

echo "🏏 PlayCricket Frontend Quick Start"
echo "===================================="
echo ""

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✅ Dependencies installed!"
    echo ""
fi

# Check if backend is running
echo "🔍 Checking backend API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running at http://localhost:8000"
else
    echo "⚠️  Backend API is not running!"
    echo "   Please start the backend first:"
    echo "   cd ../backend"
    echo "   source venv/bin/activate"
    echo "   python -m uvicorn app.main:app --reload --port 8000"
    echo ""
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🚀 Starting Angular development server..."
echo "   Frontend: http://localhost:4200"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm start
