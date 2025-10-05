#!/bin/bash

# PlayCricket Backend Setup Script
# Automates the complete development environment setup

set -e  # Exit on error

echo "🏏 PlayCricket Backend Setup"
echo "============================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Found: $PYTHON_VERSION"
else
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "🐍 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "⚡ Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✅ pip upgraded"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Setup pre-commit hooks
echo ""
echo "🔧 Setting up pre-commit hooks..."
pre-commit install
echo "✅ Pre-commit hooks installed"

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env file created from .env.example"
    echo "⚠️  Please update .env with your configuration"
else
    echo "ℹ️  .env file already exists. Skipping..."
fi

# Start Docker services
echo ""
echo "🐳 Starting Docker services (PostgreSQL + Redis)..."
if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
    docker-compose up -d postgres redis
    echo "✅ Docker services started"
    echo "   - PostgreSQL: localhost:5432"
    echo "   - Redis: localhost:6379"
    
    # Wait for PostgreSQL to be ready
    echo ""
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 5
    
    # Create test database
    echo ""
    echo "🗄️  Creating test database..."
    docker-compose exec -T postgres psql -U cricket_user -d playcricket_dev -c "CREATE DATABASE playcricket_test;" 2>/dev/null || echo "ℹ️  Test database might already exist"
    echo "✅ Test database ready"
else
    echo "⚠️  Docker not found. Please install Docker and Docker Compose."
    echo "   You can also run PostgreSQL and Redis manually."
fi

# Run database migrations
echo ""
echo "🔄 Running database migrations..."
if [ -d "alembic/versions" ]; then
    alembic upgrade head
    echo "✅ Migrations applied"
else
    echo "ℹ️  No migrations yet. Will be created as we build models."
fi

# Run tests
echo ""
echo "🧪 Running tests..."
pytest --version
echo ""
read -p "Do you want to run the initial tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pytest -v
fi

echo ""
echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Run: source venv/bin/activate"
echo "3. Run: uvicorn app.main:app --reload"
echo "4. Open http://localhost:8000/docs for API documentation"
echo ""
echo "🎯 Development workflow:"
echo "   - Write tests first (TDD): tests/models/test_*.py"
echo "   - Implement models: app/models/*.py"
echo "   - Run tests: pytest -v"
echo "   - Create migration: alembic revision --autogenerate -m 'description'"
echo "   - Apply migration: alembic upgrade head"
echo ""
echo "📚 Useful commands:"
echo "   - Start API: uvicorn app.main:app --reload"
echo "   - Run tests: pytest -v --cov=app"
echo "   - Run specific test: pytest tests/models/test_team.py -v"
echo "   - Format code: black app tests"
echo "   - Lint code: flake8 app tests"
echo "   - Type check: mypy app"
echo ""
echo "Happy coding! 🚀"