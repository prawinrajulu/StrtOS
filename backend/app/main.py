from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.redis import redis_manager
from app.core.middleware import RequestCorrelationMiddleware
from app.core.exceptions import BaseStrtOSException

# API v1 Routers
from app.auth.routes import router as auth_router
from app.api.v1.ceo import router as ceo_router
from app.api.v1.clients import router as clients_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.workflows import router as workflows_router
from app.api.v1.reports import router as reports_router
from app.api.v1.settings import router as settings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Lifespan
    setup_logging()
    logger.info("Initializing StrtOS Enterprise Backend Foundation...")
    await redis_manager.connect()
    yield
    # Shutdown Lifespan
    logger.info("Shutting down StrtOS Enterprise Backend Foundation...")
    await redis_manager.disconnect()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.9.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Request Correlation & Security Header Middleware
app.add_middleware(RequestCorrelationMiddleware)

# Global Exception Handlers
@app.exception_handler(BaseStrtOSException)
async def custom_exception_handler(request: Request, exc: BaseStrtOSException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_code": exc.__class__.__name__,
            "details": exc.details
        }
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected internal server error occurred.",
            "error_code": "InternalServerError",
            "details": {}
        }
    )

# Required Base Endpoints
@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": "0.9.0", "status": "operational"}

@app.get("/health")
async def health_check():
    redis_healthy = await redis_manager.check_health()
    return {
        "status": "healthy" if redis_healthy else "degraded",
        "redis": "connected" if redis_healthy else "disconnected",
        "version": "0.9.0"
    }

@app.get("/ready")
async def readiness_check():
    db_healthy = False
    try:
        from sqlalchemy import text
        from app.core.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_healthy = True
    except Exception:
        db_healthy = False

    if not db_healthy:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "not_ready", "database": "disconnected"})

    return {"status": "ready", "database": "connected"}

@app.get("/live")
async def liveness_check():
    return {"status": "alive"}

@app.get("/version")
async def version_info():
    return {"version": "0.9.0", "env": settings.APP_ENV}

# Include API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(ceo_router, prefix=settings.API_V1_STR)
app.include_router(clients_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(workflows_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)
