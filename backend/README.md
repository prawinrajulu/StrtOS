# StrtOS Backend Infrastructure Foundation

Enterprise-grade backend foundation for **StrtOS** built with Python 3.12, FastAPI, Pydantic v2, Async SQLAlchemy 2.0, Redis Pub/Sub, and LangGraph.

## Folder Structure

```
backend/
├── alembic/              # Alembic database migrations
├── app/
│   ├── api/v1/           # API Routers (auth, ceo, clients, dashboard, workflows, reports, settings)
│   ├── core/             # Configuration, database async engine, redis manager, security, logging, middleware
│   ├── agents/ceo/       # CEO Agent module stubs & LangGraph skeleton
│   ├── models/           # SQLAlchemy 2.0 Async DB Models
│   ├── schemas/          # Pydantic v2 validation schemas
│   ├── repositories/     # Repository Pattern implementation
│   ├── services/         # Service Layer (AuthService, etc.)
│   └── main.py           # FastAPI Application Lifespan & Global Handlers
├── Dockerfile            # Production Dockerfile
├── docker-compose.yml    # Development Docker compose (Backend + Postgres + Redis)
├── requirements.txt      # Production dependencies
└── README.md
```

## Running Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Running with Docker Compose

```bash
docker-compose up -d --build
```

## Base Endpoints

- `GET /`
- `GET /health`
- `GET /ready`
- `GET /live`
- `GET /version`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `GET /api/v1/auth/me`
