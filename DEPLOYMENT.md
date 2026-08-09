# StrtOS Production Infrastructure & Deployment Guide

This document outlines the production architecture, environment configuration, database management, Docker containerization, and security guidelines for StrtOS.

---

## 1. System Requirements & Architecture

- **Backend**: Python 3.12, FastAPI, Async SQLAlchemy, Uvicorn (ASGI)
- **Database**: Live Supabase PostgreSQL Pooler (`aws-0-ap-south-1.pooler.supabase.com:6543`)
- **Cache / Event Streaming**: Redis 7.0+
- **Frontend**: React 18, TypeScript, Vite

---

## 2. Environment Configuration

### Backend Environment Variables (`backend/.env`)
Copy `backend/.env.example` to `backend/.env`:
```env
APP_NAME=StrtOS
APP_ENV=production
DEBUG=False
API_PREFIX=/api/v1
BACKEND_PORT=8000
BACKEND_CORS_ORIGINS=["https://your-domain.com","http://localhost:5173"]

DATABASE_HOST=aws-0-ap-south-1.pooler.supabase.com
DATABASE_PORT=6543
DATABASE_NAME=postgres
DATABASE_USER=postgres.your_project_ref
DATABASE_PASSWORD=your_supabase_password
DATABASE_URL=postgresql+asyncpg://postgres.your_project_ref:your_password@aws-0-ap-south-1.pooler.supabase.com:6543/postgres

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=secure_jwt_secret_key
JWT_REFRESH_SECRET=secure_refresh_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend Environment Variables (`.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 3. Docker Deployment

Build and run using Docker Compose:
```bash
docker-compose up --build -d
```

### Backend Container Health Check
The production `backend/Dockerfile` includes automated health checking:
```bash
curl -f http://localhost:8000/health
```

---

## 4. Operational & Health Endpoints

- **Root Brief**: `GET /`
- **Health Check**: `GET /health` (Verifies Redis & process status)
- **Readiness Check**: `GET /ready` (Executes live `SELECT 1` on Supabase PostgreSQL)
- **Liveness Check**: `GET /live`
- **Version Info**: `GET /version`

---

## 5. Security Checklist
- [x] CORS restricted to explicit environment origins (`BACKEND_CORS_ORIGINS`).
- [x] Security headers enforced (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`).
- [x] JWT blacklisting enforced on Logout (`/auth/logout`).
- [x] Rate limiting active via Redis sliding window (`RateLimiter`).
- [x] All API inputs validated via Pydantic V2.
- [x] Tenant scoping (`organization_id`) enforced on all database queries.
