# 🔄 TDD Workflow Visual Guide

## The Red-Green-Refactor Cycle

```
┌──────────────────────────────────────────────────────────────────┐
│                    TEST-DRIVEN DEVELOPMENT CYCLE                  │
└──────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   🔴 RED    │  Write a failing test
    │   Phase 1   │  
    └──────┬──────┘
           │
           │  Write test first (it will fail)
           │  
           ↓
    ┌─────────────┐
    │  ❌ FAIL    │  Run test - it fails (expected!)
    │             │  
    └──────┬──────┘
           │
           │  Test fails because code doesn't exist
           │  
           ↓
    ┌─────────────┐
    │  🟢 GREEN   │  Write minimal code to pass
    │   Phase 2   │  
    └──────┬──────┘
           │
           │  Implement just enough to pass test
           │  
           ↓
    ┌─────────────┐
    │  ✅ PASS    │  Run test - it passes!
    │             │  
    └──────┬──────┘
           │
           │  Test passes, code works
           │  
           ↓
    ┌─────────────┐
    │  🔵 REFACTOR│  Improve code quality
    │   Phase 3   │  
    └──────┬──────┘
           │
           │  Clean up, optimize, improve
           │  
           ↓
    ┌─────────────┐
    │  ✅ PASS    │  Run test again - still passes!
    │             │  
    └──────┬──────┘
           │
           │  Refactoring didn't break anything
           │  
           ↓
    ┌─────────────┐
    │   COMMIT    │  Git commit
    │             │  
    └──────┬──────┘
           │
           │  Save working code
           │  
           └──────→  Next feature (back to RED)
```

---

## 🎯 Example: Team Model Implementation

### PHASE 1: RED - Write Failing Test

**File**: `tests/models/test_team.py`

```python
# ✍️ Write this FIRST (already done for you!)
def test_create_team(test_db):
    """Test creating a team."""
    team = Team(
        name="India",
        short_name="IND",
        primary_color="#0066CC",
        secondary_color="#FF9933"
    )
    # This will fail because Team doesn't exist yet!
```

**Run Test**:
```bash
pytest tests/models/test_team.py -v

# ❌ OUTPUT:
# ImportError: cannot import name 'Team' from 'app.models'
# FAILED tests/models/test_team.py::test_create_team
```

**Status**: 🔴 RED - Test fails (GOOD! This is expected!)

---

### PHASE 2: GREEN - Implement to Pass

**File**: `app/models/team.py`

```python
# ✍️ Write this to make test pass
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from ulid import ULID

class Team(Base):
    __tablename__ = "teams"
    
    public_id: Mapped[str] = mapped_column(String(26), unique=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    short_name: Mapped[str] = mapped_column(String(10), unique=True)
    primary_color: Mapped[str] = mapped_column(String(7), nullable=True)
    secondary_color: Mapped[str] = mapped_column(String(7), nullable=True)
    
    def __init__(self, **kwargs):
        if "public_id" not in kwargs:
            kwargs["public_id"] = str(ULID())
        super().__init__(**kwargs)
```

**Run Test Again**:
```bash
pytest tests/models/test_team.py -v

# ✅ OUTPUT:
# PASSED tests/models/test_team.py::test_create_team
# PASSED tests/models/test_team.py::test_unique_constraints
# PASSED tests/models/test_team.py::test_public_id_auto_generation
```

**Status**: 🟢 GREEN - All tests pass!

---

### PHASE 3: REFACTOR - Improve Code

**File**: `app/models/team.py` (improved)

```python
# ✨ Refactor: Add type hints, docstrings, methods
"""Team model for cricket teams."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from ulid import ULID
from app.models.base import Base


class Team(Base):
    """Cricket team model with ULID-based public IDs."""
    
    __tablename__ = "teams"
    
    # Public-facing ID (ULID for external API)
    public_id: Mapped[str] = mapped_column(
        String(26), 
        unique=True, 
        nullable=False,
        index=True,
        doc="External-facing ULID identifier"
    )
    
    # Team details
    name: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False,
        doc="Full team name"
    )
    short_name: Mapped[str] = mapped_column(
        String(10), 
        unique=True, 
        nullable=False,
        doc="Abbreviated team name (e.g., 'IND')"
    )
    primary_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        doc="Primary team color (hex format)"
    )
    secondary_color: Mapped[Optional[str]] = mapped_column(
        String(7),
        doc="Secondary team color (hex format)"
    )
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __init__(self, **kwargs):
        """Initialize team with auto-generated ULID if not provided."""
        if "public_id" not in kwargs:
            kwargs["public_id"] = str(ULID())
        super().__init__(**kwargs)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation for API responses."""
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
        """String representation for debugging."""
        return f"<Team(id={self.public_id}, name={self.name})>"
```

**Run Quality Checks**:
```bash
# Format code
black app/models/team.py

# Check linting
flake8 app/models/team.py

# Type check
mypy app/models/team.py

# Run tests again (ensure refactoring didn't break anything)
pytest tests/models/test_team.py -v

# ✅ OUTPUT:
# PASSED tests/models/test_team.py::test_create_team
# PASSED tests/models/test_team.py::test_unique_constraints
# PASSED tests/models/test_team.py::test_public_id_auto_generation
# PASSED tests/models/test_team.py::test_to_dict_method
```

**Status**: 🔵 REFACTOR COMPLETE - Tests still pass, code is better!

---

### PHASE 4: COMMIT

```bash
git add app/models/team.py tests/models/test_team.py
git commit -m "feat: implement Team model with ULID generation

- Add Team SQLAlchemy model with public_id (ULID)
- Add unique constraints on name and short_name
- Add to_dict() method for API serialization
- Add comprehensive tests with >95% coverage
- All tests passing"
```

---

## 📊 TDD Benefits Visual

```
┌─────────────────────────────────────────────────────────────┐
│                    WITHOUT TDD                               │
├─────────────────────────────────────────────────────────────┤
│  1. Write code ───┐                                          │
│                   │                                          │
│  2. Manually test │ (repeat many times)                      │
│                   │                                          │
│  3. Find bugs ────┘                                          │
│                                                              │
│  4. Fix bugs ─────┐                                          │
│                   │ (repeat many times)                      │
│  5. Break old code┘                                          │
│                                                              │
│  ❌ High bug rate                                            │
│  ❌ Slow development                                         │
│  ❌ Regression bugs                                          │
│  ❌ Hard to refactor                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     WITH TDD                                 │
├─────────────────────────────────────────────────────────────┤
│  1. Write test (RED)                                         │
│       ↓                                                      │
│  2. Write minimal code (GREEN)                               │
│       ↓                                                      │
│  3. Refactor (still GREEN)                                   │
│       ↓                                                      │
│  4. Commit (with confidence!)                                │
│                                                              │
│  ✅ Low bug rate (tests catch issues early)                  │
│  ✅ Fast development (clear goals)                           │
│  ✅ No regressions (tests always run)                        │
│  ✅ Safe refactoring (tests verify)                          │
│  ✅ Documentation (tests show usage)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 TDD Checklist (Use for Each Model)

### Before Starting
- [ ] Understand the model requirements
- [ ] Check related models (relationships)
- [ ] Review database schema
- [ ] Activate virtual environment

### RED Phase
- [ ] Create test file (`tests/models/test_[model].py`)
- [ ] Write test for basic creation
- [ ] Write test for unique constraints
- [ ] Write test for relationships (if any)
- [ ] Write test for methods (to_dict, etc.)
- [ ] Run tests - **they should FAIL**
- [ ] Verify failure message is what you expect

### GREEN Phase
- [ ] Create model file (`app/models/[model].py`)
- [ ] Import necessary modules (Base, Mapped, etc.)
- [ ] Define class with `__tablename__`
- [ ] Add all fields with proper types
- [ ] Add `__init__` for ULID generation
- [ ] Add relationships (if any)
- [ ] Add methods (to_dict, __repr__)
- [ ] Update `app/models/__init__.py`
- [ ] Run tests - **they should PASS**
- [ ] Check coverage (`pytest --cov`)

### REFACTOR Phase
- [ ] Add docstrings (class, methods)
- [ ] Add type hints
- [ ] Add field documentation
- [ ] Optimize code structure
- [ ] Run `black` to format
- [ ] Run `flake8` to lint
- [ ] Run `mypy` for type checking
- [ ] Run tests again - **still PASS**
- [ ] Check coverage is >90%

### COMMIT Phase
- [ ] Review changes (`git diff`)
- [ ] Stage files (`git add`)
- [ ] Write descriptive commit message
- [ ] Commit (`git commit`)
- [ ] Push to remote (optional)

### MIGRATION Phase
- [ ] Generate migration (`alembic revision --autogenerate`)
- [ ] Review migration file
- [ ] Apply migration (`alembic upgrade head`)
- [ ] Verify in database

---

## 🚦 Common TDD Mistakes to Avoid

### ❌ DON'T:
```python
# ❌ Writing implementation first
class Team(Base):  # <- WRONG! Write test first!
    name: Mapped[str] = ...

# ❌ Writing tests after implementation
def test_team():  # <- Too late! Should be first!
    assert team.name == "India"

# ❌ Not running tests frequently
# (Writing lots of code before testing)

# ❌ Skipping RED phase
# (Tests pass immediately - you're not testing anything!)

# ❌ Not refactoring
# (Code works but is messy)
```

### ✅ DO:
```python
# ✅ Write test FIRST (RED)
def test_create_team(test_db):
    team = Team(name="India")  # This will fail!
    assert team.name == "India"

# ✅ Run test (see it fail)
pytest tests/models/test_team.py  # ❌ FAILS

# ✅ Implement minimal code (GREEN)
class Team(Base):
    name: Mapped[str] = mapped_column(String(100))

# ✅ Run test again (passes)
pytest tests/models/test_team.py  # ✅ PASSES

# ✅ Refactor (improve code)
class Team(Base):
    """Cricket team model."""  # Added docstring
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,  # Added constraint
        doc="Team name"  # Added documentation
    )

# ✅ Test still passes
pytest tests/models/test_team.py  # ✅ STILL PASSES
```

---

## 📈 Progress Tracking

Use this to track your model implementation progress:

```
[ ] Team      - 🔴 RED → 🟢 GREEN → 🔵 REFACTOR → ✅ COMMITTED
[ ] Player    - 🔴 RED → 🟢 GREEN → 🔵 REFACTOR → ✅ COMMITTED
[ ] Venue     - 🔴 RED → 🟢 GREEN → 🔵 REFACTOR → ✅ COMMITTED
[ ] Official  - 🔴 RED → 🟢 GREEN → 🔵 REFACTOR → ✅ COMMITTED
[ ] Tournament- 🔴 RED → 🟢 GREEN → 🔵 REFACTOR → ✅ COMMITTED
[ ] Match     - 🔴 RED → 🟢 GREEN → 🔵 REFACTOR → ✅ COMMITTED
[ ] Innings   - 🔴 RED → 🟢 GREEN → 🔵 REFACTOR → ✅ COMMITTED
[ ] Delivery  - 🔴 RED → 🟢 GREEN → 🔵 REFACTOR → ✅ COMMITTED
```

---

## 🎓 TDD Mantras

> **"Red, Green, Refactor"**
> 
> **"Test First, Code Second"**
> 
> **"Make it Fail, Make it Pass, Make it Better"**
> 
> **"Write the test you wish you had"**
> 
> **"If it's not tested, it's broken"**

---

## 🚀 Ready to Start?

1. Run `cd backend && ./setup.sh`
2. Activate venv: `source venv/bin/activate`
3. See Team tests fail: `pytest tests/models/test_team.py -v`
4. Implement Team model in `app/models/team.py`
5. See tests pass: `pytest tests/models/test_team.py -v`
6. Refactor and commit
7. Repeat for next model!

**Remember**: Red → Green → Refactor → Commit → Repeat! 🔄
