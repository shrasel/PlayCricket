# 🎯 YOUR NEXT STEPS - Start Here!

## 📍 Current Status

✅ **COMPLETED**: Backend infrastructure setup
- FastAPI project structure created
- Docker Compose configured (PostgreSQL + Redis)
- Testing framework ready (pytest with async support)
- First TDD test written (`tests/models/test_team.py`)
- Development guide created
- Automated setup script ready

🔨 **NOW**: Implement Team model following TDD workflow

---

## 🚀 Step-by-Step Guide

### Step 1: Environment Setup (5 minutes)

```bash
# Navigate to backend directory
cd backend

# Run automated setup script
./setup.sh

# This script will:
# - Create Python virtual environment
# - Install all dependencies
# - Start Docker services (PostgreSQL + Redis)
# - Copy environment configuration
# - Install pre-commit hooks
# - Run initial tests (Team tests will FAIL - that's expected!)
```

**Expected Output**: You should see test failures for Team model (RED phase ✅)

---

### Step 2: Activate Virtual Environment

```bash
# Activate the virtual environment
source venv/bin/activate

# Verify activation (should show path to venv)
which python
```

---

### Step 3: TDD Red Phase - Run Failing Tests

```bash
# Run Team model tests (they will fail - this is correct!)
pytest tests/models/test_team.py -v

# Expected output:
# ❌ ImportError: cannot import name 'Team' from 'app.models'
# This is the RED phase - tests fail because model doesn't exist yet
```

---

### Step 4: TDD Green Phase - Implement Team Model

Create the file `app/models/team.py`:

```python
"""Team model for cricket teams."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from ulid import ULID
from app.models.base import Base


class Team(Base):
    """Cricket team model."""
    
    __tablename__ = "teams"
    
    # Public-facing ID (ULID for external API)
    public_id: Mapped[str] = mapped_column(
        String(26), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    # Team details
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    short_name: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    primary_color: Mapped[Optional[str]] = mapped_column(String(7))  # Hex color
    secondary_color: Mapped[Optional[str]] = mapped_column(String(7))
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    def __init__(self, **kwargs):
        """Initialize team with auto-generated ULID."""
        if "public_id" not in kwargs:
            kwargs["public_id"] = str(ULID())
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.public_id,
            "name": self.name,
            "short_name": self.short_name,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "logo_url": self.logo_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self) -> str:
        return f"<Team(id={self.public_id}, name={self.name})>"
```

Also create `app/models/__init__.py`:

```python
"""Models package."""
from app.models.base import Base
from app.models.team import Team

__all__ = ["Base", "Team"]
```

And create `app/models/base.py`:

```python
"""Base model for all database models."""
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    # Primary key (internal use only)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
```

---

### Step 5: TDD Green Phase - Run Tests Again

```bash
# Run tests again
pytest tests/models/test_team.py -v

# Expected output:
# ✅ test_create_team PASSED
# ✅ test_team_unique_constraints PASSED
# ✅ test_public_id_auto_generation PASSED
# ✅ test_to_dict_method PASSED

# This is the GREEN phase - all tests pass!
```

---

### Step 6: TDD Refactor Phase - Code Quality

```bash
# Format code
black app tests

# Check linting
flake8 app tests

# Type checking
mypy app

# Run tests again to ensure refactoring didn't break anything
pytest tests/models/test_team.py -v
```

---

### Step 7: Create Database Migration

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Configure alembic/env.py (add these imports and settings)
# See DEV_GUIDE.md for detailed configuration

# Generate migration
alembic revision --autogenerate -m "Add team model"

# Review the generated migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Verify
alembic current
```

---

### Step 8: Start API Server

```bash
# Run FastAPI development server
uvicorn app.main:app --reload --log-level debug

# Visit in browser:
# API Docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## 📚 What You Just Accomplished

✅ **Environment**: Set up complete development environment
✅ **TDD Red**: Wrote tests first (they failed)
✅ **TDD Green**: Implemented model to pass tests
✅ **TDD Refactor**: Applied code quality tools
✅ **Migration**: Created database schema from model
✅ **Server**: Started API server

---

## 🎯 Next Models to Implement (in order)

1. **Player** - Follows same TDD pattern
   - Write tests in `tests/models/test_player.py`
   - Implement `app/models/player.py`
   - Add relationship to Team (ForeignKey)

2. **Venue** - Stadium/ground information
   - Write tests in `tests/models/test_venue.py`
   - Implement `app/models/venue.py`

3. **Official** - Umpires and match officials
   - Write tests in `tests/models/test_official.py`
   - Implement `app/models/official.py`

4. **Tournament** - League/tournament information
   - Write tests in `tests/models/test_tournament.py`
   - Implement `app/models/tournament.py`

5. **Match** - Most complex model
   - Write tests in `tests/models/test_match.py`
   - Implement `app/models/match.py`
   - Multiple relationships (Team, Venue, Tournament, Officials)

6. **Innings** - Match innings
   - Write tests in `tests/models/test_innings.py`
   - Implement `app/models/innings.py`

7. **Delivery** - Ball-by-ball records (MOST CRITICAL!)
   - Write tests in `tests/models/test_delivery.py`
   - Implement `app/models/delivery.py`
   - This is the core of the platform

---

## 📖 Resources

- **[DEV_GUIDE.md](backend/DEV_GUIDE.md)** - Complete TDD workflow guide
- **[backend/README.md](backend/README.md)** - Backend quick reference
- **[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md)** - Full 10-week roadmap
- **[Docker Compose](backend/docker-compose.yml)** - Database configuration
- **[API Schemas](api/)** - DTO definitions for reference

---

## ⚡ Quick Commands Reference

```bash
# Run tests
pytest -v
pytest tests/models/test_team.py -v    # Specific file
pytest --cov=app --cov-report=html     # With coverage

# Database
docker-compose up -d                    # Start services
docker-compose logs -f postgres         # View logs
alembic upgrade head                    # Apply migrations
alembic revision --autogenerate -m "msg"  # Create migration

# Server
uvicorn app.main:app --reload          # Development
uvicorn app.main:app --workers 4       # Production

# Code Quality
black app tests                         # Format
flake8 app tests                        # Lint
mypy app                                # Type check
pre-commit run --all-files             # All checks

# Docker Database Shell
docker exec -it playcricket-postgres psql -U cricket -d cricketdb
```

---

## 🎨 Development Workflow (Repeat for Each Model)

```
1. Write Test (RED)
   ↓
2. Run Test (FAILS)
   ↓
3. Implement Model (GREEN)
   ↓
4. Run Test (PASSES)
   ↓
5. Refactor Code
   ↓
6. Run Test (STILL PASSES)
   ↓
7. Create Migration
   ↓
8. Commit to Git
   ↓
9. Move to Next Model
```

---

## 🚨 Common Issues & Solutions

### Issue: Tests fail with "no such table"
**Solution**: Run `alembic upgrade head` to create tables

### Issue: Import errors for models
**Solution**: Ensure `app/models/__init__.py` exports the model

### Issue: Docker services not starting
**Solution**: 
```bash
docker-compose down -v
docker-compose up -d
docker-compose logs -f
```

### Issue: ULID import error
**Solution**: `pip install python-ulid`

### Issue: Black/flake8 conflicts
**Solution**: Configuration already set in `setup.cfg` and `.pre-commit-config.yaml`

---

## 🎯 Success Criteria

Before moving to API endpoints, you should have:

- ✅ All 7 core models implemented with tests
- ✅ All tests passing with >90% coverage
- ✅ All Alembic migrations applied
- ✅ Code quality checks passing (black, flake8, mypy)
- ✅ Models properly export relationships
- ✅ FastAPI server running without errors

---

## 💪 You're Ready!

Run `cd backend && ./setup.sh` and start with the Team model. Follow the TDD workflow strictly:

**RED → GREEN → REFACTOR**

Good luck! 🚀
