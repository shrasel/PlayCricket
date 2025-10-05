# 🏏 PlayCricket Backend - Development Guide

## 🚀 Quick Start

```bash
# 1. Run setup script (recommended)
cd backend
./setup.sh

# 2. Manual setup (alternative)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker-compose up -d
cp .env.example .env
```

## 📝 TDD Development Workflow

We follow **Test-Driven Development (TDD)** with the Red-Green-Refactor cycle:

### 1. RED - Write Failing Test
```bash
# Create test file first
touch tests/models/test_team.py

# Write test cases that define expected behavior
pytest tests/models/test_team.py -v
# ❌ Tests should FAIL (model doesn't exist yet)
```

###  2. GREEN - Make Test Pass
```bash
# Implement the model to make tests pass
touch app/models/team.py

# Run tests again
pytest tests/models/test_team.py -v
# ✅ Tests should PASS
```

### 3. REFACTOR - Improve Code
```bash
# Optimize, clean up, add features
black app tests
flake8 app tests
mypy app

# Tests should still pass
pytest tests/models/test_team.py -v
```

---

## 🎯 Phase-by-Phase Development

### **PHASE 1: Database Models (Week 1)**

#### Step 1: Team Model (TDD)
```bash
# 1. Write tests
vim tests/models/test_team.py

# 2. Run tests (should fail)
pytest tests/models/test_team.py -v

# 3. Implement model
vim app/models/team.py

# 4. Run tests (should pass)
pytest tests/models/test_team.py -v

# 5. Create migration
alembic revision --autogenerate -m "Add team model"
alembic upgrade head
```

**Team Model Requirements**:
- [x] Auto-generate ULID for public_id
- [x] Unique constraints on name and short_name
- [x] Optional logo_url, colors
- [x] Created timestamp
- [x] to_dict() method for serialization

#### Step 2: Player Model (TDD)
```bash
pytest tests/models/test_player.py -v  # RED
vim app/models/player.py                # GREEN
pytest tests/models/test_player.py -v  # GREEN
alembic revision --autogenerate -m "Add player model"
```

**Player Model Requirements**:
- Full name, known_as (display name)
- Date of birth
- Batting style (RHB/LHB)
- Bowling style (RF, SLA, LBG, etc.)
- Nationality

#### Step 3: Venue, Official, Tournament Models
Follow same TDD pattern for each model.

#### Step 4: Match & Innings Models
Complex models with relationships - write extensive tests.

#### Step 5: Delivery Model (Most Important!)
```bash
# This is the core of live scoring
pytest tests/models/test_delivery.py -v

# Test cases must cover:
# - Legal vs illegal deliveries
# - Ball sequencing (over_number, ball_in_over)
# - Runs split (runs_batter vs runs_extras)
# - Wicket types
# - Boundary detection
# - Wagon wheel coordinates
```

---

### **PHASE 2: Repository Pattern (Week 2)**

#### Repository Structure
```python
app/repositories/
├── base.py          # Generic CRUD operations
├── team.py          # Team-specific queries
├── player.py        # Player-specific queries
├── match.py         # Match operations
├── delivery.py      # Delivery recording
└── stats.py         # Analytics queries
```

#### TDD for Repositories
```bash
# 1. Write repository tests
vim tests/repositories/test_team_repository.py

# Test cases:
# - Create team
# - Get team by ID/public_id
# - List teams with pagination
# - Update team
# - Delete team
# - Search teams by name

# 2. Run tests (fail)
pytest tests/repositories/test_team_repository.py -v

# 3. Implement repository
vim app/repositories/team.py

# 4. Tests pass
pytest tests/repositories/test_team_repository.py -v
```

---

### **PHASE 3: API Endpoints (Week 2-3)**

#### TDD for FastAPI Endpoints
```bash
# 1. Write endpoint tests
vim tests/api/test_teams.py

# Use FastAPI TestClient
@pytest.mark.asyncio
async def test_create_team(client):
    response = await client.post("/api/teams", json={
        "name": "Mumbai Indians",
        "short_name": "MI"
    })
    assert response.status_code == 201
    assert response.json()["data"]["name"] == "Mumbai Indians"

# 2. Implement endpoint
vim app/api/v1/endpoints/teams.py

# 3. Register router
vim app/main.py  # Include router
```

#### API Development Order
1. **Teams API** - CRUD operations
2. **Players API** - With team relationships
3. **Matches API** - Create, list, filter
4. **Live Scoring API** - Delivery recording
5. **Scorecard API** - Analytics endpoints
6. **Tournament API** - League tables, NRR

---

### **PHASE 4: Live Scoring (Week 3)**

#### Critical Endpoints
```python
POST /api/deliveries
{
  "innings_public_id": "01HP...",
  "over_number": 0,
  "ball_in_over": 1,
  "striker_public_id": "01HP...",
  "bowler_public_id": "01HP...",
  "runs_batter": 4,
  "is_four": true
}

GET /api/matches/{id}/live
# Real-time match center data

WS /ws/matches/{id}
# WebSocket for live updates
```

#### Performance Testing
```bash
# Load testing with locust
locust -f tests/load/test_delivery_recording.py

# Target: 1000+ deliveries per second
# Response time: <50ms p95
```

---

## 🧪 Testing Best Practices

### Test Structure
```python
# tests/models/test_team.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
@pytest.mark.unit  # or integration, e2e
class TestTeamModel:
    async def test_create_team(self, test_db: AsyncSession):
        """Test description"""
        # Arrange
        team_data = {...}
        
        # Act
        team = Team(**team_data)
        test_db.add(team)
        await test_db.commit()
        
        # Assert
        assert team.id is not None
```

### Running Tests
```bash
# All tests
pytest -v

# Specific test file
pytest tests/models/test_team.py -v

# Specific test class
pytest tests/models/test_team.py::TestTeamModel -v

# Specific test function
pytest tests/models/test_team.py::TestTeamModel::test_create_team -v

# With coverage
pytest --cov=app --cov-report=html

# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Parallel execution
pytest -n auto
```

---

## 🗄️ Database Migrations

### Alembic Workflow
```bash
# Initialize (already done)
alembic init alembic

# Create migration after model changes
alembic revision --autogenerate -m "Add team model"

# Review migration file
vim alembic/versions/xxx_add_team_model.py

# Apply migration
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>

# View current version
alembic current

# View migration history
alembic history
```

---

## 📊 Performance Optimization

### Query Optimization
```python
# Use select_in_load for relationships
from sqlalchemy.orm import selectinload

teams = await session.execute(
    select(Team)
    .options(selectinload(Team.players))
    .limit(10)
)

# Add indexes in models
__table_args__ = (
    Index('ix_team_name_trgm', 'name', postgresql_using='gin'),
)
```

### Caching Strategy
```python
from app.core.cache import redis_client

# Cache function results
async def get_team(public_id: str):
    # Try cache first
    cached = await redis_client.get(f"team:{public_id}")
    if cached:
        return cached
    
    # Query database
    team = await repository.get_by_public_id(public_id)
    
    # Cache result
    await redis_client.set(f"team:{public_id}", team.to_dict(), ttl=300)
    return team
```

---

## 🔍 Code Quality

### Run All Checks
```bash
# Format code
black app tests

# Sort imports
isort app tests

# Lint
flake8 app tests

# Type check
mypy app

# Security check
bandit -r app

# All in one
black app tests && isort app tests && flake8 app tests && mypy app
```

### Pre-commit Hooks
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

---

## 🐛 Debugging

### FastAPI Debug Mode
```python
# app/main.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use debugger
import debugpy
debugpy.listen(5678)
```

### Database Query Debugging
```python
# Enable SQL echo
engine = create_async_engine(
    DATABASE_URL,
    echo=True  # Print all SQL queries
)
```

### Redis Debugging
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# View all keys
KEYS *

# Get value
GET "team:01HP..."

# Monitor commands
MONITOR
```

---

## 📈 Next Steps

After completing backend:
1. ✅ All models implemented with >90% test coverage
2. ✅ Repository pattern for all data access
3. ✅ Core API endpoints functional
4. ✅ WebSocket live updates working
5. ✅ Performance targets met (<50ms API response)

**Then move to Frontend (Angular)**:
- Angular workspace setup
- Core services (HTTP, WebSocket)
- Live match center UI
- Charts and analytics components
- Scorer admin panel

---

## 🆘 Common Issues

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Docker Issues
```bash
# Reset everything
docker-compose down -v
docker-compose up -d
```

### Migration Conflicts
```bash
# Reset database
alembic downgrade base
alembic upgrade head
```

---

Happy coding! 🚀 Follow TDD and you'll build a solid, testable codebase!