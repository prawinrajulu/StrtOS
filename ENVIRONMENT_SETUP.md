# StrtOS Centralized Environment Configuration Setup

This document provides setup instructions for environment configuration across Local Development, Staging, Production, and Docker environments.

---

## 1. Required Variables Checklist

| Variable Name | Category | Default / Required | Description |
| :--- | :--- | :--- | :--- |
| `APP_NAME` | Application | `StrtOS` | Application Title |
| `APP_ENV` | Application | `development` / `production` | Environment tier |
| `DEBUG` | Application | `True` / `False` | Debug mode toggle |
| `API_PREFIX` | Application | `/api/v1` | REST API prefix |
| `BACKEND_PORT` | Application | `8000` | FastAPI server port |
| `FRONTEND_PORT` | Application | `5173` | Vite dev server port |
| `DATABASE_HOST` | Database | `localhost` | PostgreSQL host |
| `DATABASE_PORT` | Database | `5432` | PostgreSQL port |
| `DATABASE_NAME` | Database | `strtos_db` | Database name |
| `DATABASE_USER` | Database | `postgres` | Database user |
| `DATABASE_PASSWORD` | Database | `postgres` | Database password |
| `DATABASE_URL` | Database | Auto-assembled | Full async PostgreSQL connection URL |
| `REDIS_HOST` | Redis | `localhost` | Redis host |
| `REDIS_PORT` | Redis | `6379` | Redis port |
| `REDIS_DB` | Redis | `0` | Redis database index |
| `REDIS_URL` | Redis | Auto-assembled | Full Redis connection URL |
| `JWT_SECRET_KEY` | JWT Security | **Required** | Secret key for access tokens |
| `JWT_REFRESH_SECRET` | JWT Security | **Required** | Secret key for refresh tokens |
| `JWT_ALGORITHM` | JWT Security | `HS256` | Token signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT Security | `15` | Access token lifespan |
| `REFRESH_TOKEN_EXPIRE_DAYS` | JWT Security | `7` | Refresh token lifespan |
| `OPENAI_API_KEY` | AI Provider | Optional | OpenAI API key |
| `GEMINI_API_KEY` | AI Provider | Optional | Gemini API key |
| `ANTHROPIC_API_KEY` | AI Provider | Optional | Anthropic API key |
| `FIRECRAWL_API_KEY` | Tool | Optional | Web Scraper tool API key |
| `TAVILY_API_KEY` | Tool | Optional | Search tool API key |
| `SERPER_API_KEY` | Tool | Optional | Serper Google Search key |

---

## 2. Local Development Setup

1. Copy `.env.development` to `.env`:
   ```bash
   cp .env.development .env
   ```
2. Copy `frontend/.env.development` to `frontend/.env`:
   ```bash
   cp frontend/.env.development frontend/.env
   ```
3. Run Backend:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

---

## 3. Production Deployment

1. Set `APP_ENV=production` and `DEBUG=False`.
2. Generate secure 64-byte random secrets for `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET`:
   ```bash
   openssl rand -hex 32
   ```
3. Supply valid production `DATABASE_URL` and `REDIS_URL`.
4. Production fail-fast checks in `app/core/config.py` will block execution if insecure placeholder secrets are detected.

---

## 4. Security Notes

- **Never commit `.env` or `.env.local` to Git repositories.** `.gitignore` is configured to ignore all `.env` files except `.env.example`.
- Keep API keys stored in encrypted secret managers (AWS Secrets Manager, HashiCorp Vault, or GitHub Secrets) during deployment.
