<div align="center">

# 🏏 PlayCricket

### Professional Cricket Management, Live Scoring, and Analytics Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Angular](https://img.shields.io/badge/Angular-18.2-DD0031?style=flat-square&logo=angular)](https://angular.io/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7+-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

Modern full-stack platform for live cricket scoring, tournament management, and advanced analytics across Test, ODI, T20, T10, and The Hundred.

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [API](#-api-overview) • [Development](#-development) • [Testing](#-testing) • [Deployment](#-docker--deployment) • [Contributing](#-contributing)

</div>

---

## 📋 Overview

PlayCricket delivers professional-grade cricket operations:

- ⚡ Real-time live scoring with WebSockets
- 📊 Advanced analytics: scorecards, Manhattan, Wagon wheel, partnerships
- 🏆 Tournament management with NRR and multi-stage formats
- 🔒 Role-based access and secure authentication
- 🧱 Scalable backend with async SQLAlchemy and Redis caching

---

## ✨ Features

- Ball-by-ball scoring with non-destructive corrections
- Live scorecards computed from deliveries (no duplicated totals)
- Player and team management, venues, tournaments
- DLS handling, extras, wickets, milestones, partnerships
- Type-safe DTOs on the frontend; OpenAPI docs on the backend

---

## 🧰 Tech Stack

- Backend: FastAPI 0.115.0, SQLAlchemy 2.x (async), Alembic, Redis 7, PostgreSQL 15+
- Frontend: Angular 18.2, TypeScript 5.5, RxJS, Tailwind (config present)
- Dev: Docker Compose, pytest, Black/Flake8/mypy, ESLint/Prettier

---

## 🧭 Project Structure

```
playcricket/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI app + middleware + routers
│   │   ├── core/                 # config, database, cache, security
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   └── api/                  # API routes
│   ├── alembic/                  # DB migrations
│   ├── docker-compose.yml        # Postgres + Redis (dev)
│   ├── requirements.txt          # Python deps
│   ├── .env.example              # Backend env template
│   └── README.md                 # Backend docs
├── frontend/                     # Angular frontend
│   ├── package.json              # npm scripts (start, build, test)
│   └── src/app/                  # Angular app sources
├── migrations/                   # SQL schema files (views, seeds)
├── QUICK_START.md                # Quick start guide
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Docker and Docker Compose

### 1) Backend (API)

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start services: PostgreSQL + Redis
docker-compose up -d

# Configure environment
cp .env.example .env

# Apply migrations
alembic upgrade head

# Run API (http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```

Docs: http://localhost:8000/docs • ReDoc: http://localhost:8000/redoc • Health: http://localhost:8000/health

### 2) Frontend (Web)

```bash
cd frontend
npm install
npm start
```

App: http://localhost:4200

---

## 🏗 Architecture

```
Angular (HTTP/WebSocket)
    │
    ▼
FastAPI (routers ↔ services ↔ SQLAlchemy async)
    ├── PostgreSQL (primary data + views)
    └── Redis (cache, sessions, real-time aux)
```

Design principles:

- Data integrity: strict FK, enum tables, ULID public IDs
- Performance: computed views, strategic indexes, caching
- Real-time: WebSockets for live updates; REST for queries
- Security: JWT, CORS, configurable origins

---

## 🔌 API Overview

- Base URL (dev): `http://localhost:8000`
- Prefix: `/api` (configurable via `API_V1_PREFIX`)

Examples:

```http
GET /api/teams
GET /api/players
GET /api/matches/{id}
GET /api/matches/{id}/scorecard
POST /api/deliveries
```

Web: Swagger UI at `/docs` • Health at `/health`

---

## ⚙️ Environment (backend/.env)

Use `backend/.env.example` as a template. Key settings:

```env
# Application
APP_NAME=PlayCricket API
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Database (matches docker-compose services)
DATABASE_URL=postgresql+asyncpg://cricket_user:cricket_pass_dev@localhost:5432/playcricket_dev
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_ECHO=False

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=300

# Security
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:4200","http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=True

# API
API_V1_PREFIX=/api
DOCS_URL=/docs
REDOC_URL=/redoc
```

---

## 🧪 Testing

```bash
cd backend
source venv/bin/activate

# Run tests
pytest -v

# Coverage
pytest --cov=app --cov-report=html
```

---

## 🧱 Migrations

```bash
cd backend

# Create a new migration from model changes
alembic revision --autogenerate -m "Describe changes"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

---

## 🐳 Docker • Deployment

- Dev services are defined in `backend/docker-compose.yml` (PostgreSQL + Redis)
- Run `docker-compose up -d` from the `backend/` directory
- For production, containerize backend/frontend separately and front with Nginx

Example (backend image):

```bash
cd backend
docker build -t playcricket-backend .
docker run -p 8000:8000 playcricket-backend
```

---

## 🗂 Documentation

- Quick start: `QUICK_START.md`
- Backend guide: `backend/DEV_GUIDE.md`
- Backend details: `backend/README.md`
- Frontend details: `frontend/README.md`

---

## 🤝 Contributing

- Write tests for new features and bug fixes
- Use Black/Flake8/mypy for Python; ESLint/Prettier for TS
- Keep documentation up to date

---

## 📜 License

No license file is present. Consider adding MIT or Apache-2.0.

