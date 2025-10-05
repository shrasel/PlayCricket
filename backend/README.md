# Cricket Platform Backend API

FastAPI-based high-performance backend with async SQLAlchemy, Redis caching, and WebSocket support.

## 🚀 Quick Start

```bash
# Automated setup (recommended)
./setup.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d
cp .env.example .env

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Visit
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app + lifespan
│   ├── core/
│   │   ├── config.py          # Settings (from .env)
│   │   ├── database.py        # Async SQLAlchemy
│   │   └── cache.py           # Redis wrapper
│   ├── models/                # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py            # Base class
│   │   ├── team.py            # Team model
│   │   ├── player.py          # Player model
│   │   ├── match.py           # Match model
│   │   └── delivery.py        # Delivery (ball-by-ball)
│   ├── repositories/          # Data access layer
│   │   ├── base.py            # BaseRepository
│   │   └── team.py            # TeamRepository
│   ├── schemas/               # Pydantic DTOs
│   │   └── team.py            # TeamCreate, TeamRead, etc.
│   └── api/                   # API endpoints
│       └── v1/
│           ├── teams.py       # Team CRUD
│           ├── matches.py     # Match endpoints
│           └── live.py        # WebSocket live updates
├── tests/
│   ├── conftest.py            # pytest fixtures
│   ├── models/                # Model tests
│   ├── repositories/          # Repository tests
│   └── api/                   # API endpoint tests
├── alembic/                   # Database migrations
├── docker-compose.yml         # PostgreSQL + Redis
├── requirements.txt           # Dependencies
├── pytest.ini                 # Test config
├── .env.example               # Environment template
└── DEV_GUIDE.md              # Development workflow
```

## 🧪 Testing (TDD)

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/models/test_team.py -v

# Run tests matching pattern
pytest -k "team" -v

# Watch mode (requires pytest-watch)
ptw
```

### TDD Workflow

1. **RED**: Write failing test
   ```bash
   vim tests/models/test_player.py
   pytest tests/models/test_player.py  # ❌ FAILS
   ```

2. **GREEN**: Implement to pass
   ```bash
   vim app/models/player.py
   pytest tests/models/test_player.py  # ✅ PASSES
   ```

3. **REFACTOR**: Optimize
   ```bash
   black app tests
   pytest tests/models/test_player.py  # ✅ STILL PASSES
   ```

## 🗃️ Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Configure env.py (see DEV_GUIDE.md)

# Auto-generate migration from models
alembic revision --autogenerate -m "Add player model"

# Review migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Check current version
alembic current

# View migration history
alembic history --verbose
```

## 🐳 Docker Services

```bash
# Start PostgreSQL + Redis
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Reset database (⚠️ destroys data)
docker-compose down -v
docker-compose up -d
```

### Service URLs
- **PostgreSQL**: `localhost:5432` (user: `cricket`, db: `cricketdb`)
- **Redis**: `localhost:6379`
- **API Docs**: `http://localhost:8000/docs`
- **Coverage Report**: `htmlcov/index.html`

## 🔧 Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql+asyncpg://cricket:cricket123@localhost:5432/cricketdb

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:4200,http://localhost:3000

# Environment
ENVIRONMENT=development
DEBUG=True

# Performance
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
REDIS_MAX_CONNECTIONS=50
```

## 📡 API Endpoints (Planned)

### Teams
```
GET    /api/v1/teams              # List teams
POST   /api/v1/teams              # Create team
GET    /api/v1/teams/{id}         # Get team
PUT    /api/v1/teams/{id}         # Update team
DELETE /api/v1/teams/{id}         # Delete team
GET    /api/v1/teams/{id}/players # Team roster
```

### Matches
```
GET    /api/v1/matches            # List matches
POST   /api/v1/matches            # Create match
GET    /api/v1/matches/{id}       # Get match details
GET    /api/v1/matches/{id}/scorecard  # Full scorecard
GET    /api/v1/matches/{id}/commentary # Ball-by-ball
WS     /api/v1/matches/{id}/live  # WebSocket live updates
```

### Live Scoring
```
POST   /api/v1/deliveries         # Record delivery
PUT    /api/v1/deliveries/{id}    # Correct delivery
POST   /api/v1/innings/end        # End innings
POST   /api/v1/matches/{id}/result # Set match result
```

## 🎯 Code Quality

```bash
# Format code
black app tests

# Lint
flake8 app tests

# Type checking
mypy app

# All checks (pre-commit)
pre-commit run --all-files

# Install pre-commit hooks
pre-commit install
```

## 📊 Performance Monitoring

```bash
# Profile API endpoint
python -m cProfile -o profile.stats -m uvicorn app.main:app

# Analyze with snakeviz
pip install snakeviz
snakeviz profile.stats

# Database query logging (set in .env)
SQLALCHEMY_ECHO=True
```

## 🔥 Common Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Install new dependency
pip install package-name
pip freeze > requirements.txt

# Run development server with auto-reload
uvicorn app.main:app --reload --log-level debug

# Run production server (multi-worker)
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Interactive Python shell with app context
python -c "from app.core.database import AsyncSessionLocal; import asyncio"

# Database shell
docker exec -it playcricket-postgres psql -U cricket -d cricketdb
```

## 🐛 Debugging

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()

# Run tests with pdb on failure
pytest --pdb
```

## 📚 Key Dependencies

- **FastAPI 0.104+**: Modern async web framework
- **SQLAlchemy 2.0+**: Async ORM with new API
- **Alembic**: Database migration tool
- **asyncpg**: High-performance PostgreSQL driver
- **redis-py**: Redis client with async support
- **pytest-asyncio**: Async test support
- **Pydantic 2.0+**: Data validation
- **python-ulid**: ULID generation for public IDs
- **orjson**: Fast JSON serialization

## 🚦 Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/health/db

# Redis connection
curl http://localhost:8000/health/redis
```

## 📖 Further Reading

- [DEV_GUIDE.md](./DEV_GUIDE.md) - Complete TDD workflow
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [pytest Docs](https://docs.pytest.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

**Next Step**: Run `./setup.sh` then implement `app/models/team.py` to pass the tests in `tests/models/test_team.py`! 🎯