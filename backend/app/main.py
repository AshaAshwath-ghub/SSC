"""
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uuid

from app.core.config import settings
from app.core.logging import setup_logging, get_logger, request_id_ctx
from app.db.adapters import init_database, close_database
from app.db.mongodb import mongodb
from app.db.redis import redis_manager
from app.api.auth import router as auth_router
from app.api.oauth import router as oauth_router
from app.api.admin import router as admin_router


# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database type: {settings.db_type}")

    try:
        # Initialize database connections
        logger.info("Initializing database connections...")
        await init_database()
        await mongodb.connect()
        await redis_manager.connect()
        logger.info("All database connections initialized successfully")

        yield

    finally:
        # Shutdown
        logger.info("Shutting down application...")
        await close_database()
        await mongodb.close()
        await redis_manager.close()
        logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Full-stack application with FastAPI backend",
    version=settings.app_version,
    docs_url=f"{settings.api_prefix}/docs" if settings.debug else None,
    redoc_url=f"{settings.api_prefix}/redoc" if settings.debug else None,
    openapi_url=f"{settings.api_prefix}/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)


# Middleware
@app.middleware("http")
async def add_request_id(request, call_next):
    """Add unique request ID to each request for tracing."""
    request_id = str(uuid.uuid4())
    request_id_ctx.set(request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.url.path}")

    response = await call_next(request)

    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Include routers
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(oauth_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id_ctx.get(""),
        },
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running",
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Checks connectivity to all services.
    """
    from app.db.adapters import get_database_adapter

    health_status = {
        "status": "healthy",
        "version": settings.app_version,
        "environment": settings.environment,
        "services": {}
    }

    # Check SQL database
    try:
        db_adapter = get_database_adapter()
        sql_healthy = await db_adapter.health_check()
        health_status["services"]["sql_database"] = {
            "status": "healthy" if sql_healthy else "unhealthy",
            "type": db_adapter.db_type,
        }
    except Exception as e:
        logger.error(f"SQL database health check failed: {e}")
        health_status["services"]["sql_database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # Check MongoDB
    try:
        mongo_healthy = await mongodb.health_check()
        health_status["services"]["mongodb"] = {"status": "healthy" if mongo_healthy else "unhealthy"}
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        health_status["services"]["mongodb"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # Check Redis
    try:
        redis_healthy = await redis_manager.health_check()
        health_status["services"]["redis"] = {"status": "healthy" if redis_healthy else "unhealthy"}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(status_code=status_code, content=health_status)


# Ready check for Kubernetes
@app.get("/ready")
async def ready_check():
    """Readiness check for Kubernetes."""
    return {"status": "ready"}


# Liveness check for Kubernetes
@app.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes."""
    return {"status": "alive"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_config=None,  # Use our custom logging
    )
