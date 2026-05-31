import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import connect_db, close_db

# Routes will be imported here in later phases
# from app.routes import auth, transactions, dashboard

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager for application startup and shutdown.
    FastAPI's recommended replacement for on_event decorators.
    """
    logger.info("Starting up %s v%s …", settings.app_name, settings.app_version)
    await connect_db()
    yield
    logger.info("Shutting down …")
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API for tracking personal income and expenses.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — tighten allowed_origins for production
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Replace with exact frontend origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Health check — always available, no auth required
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


# ---------------------------------------------------------------------------
# Routers — uncomment as phases are completed
# ---------------------------------------------------------------------------
# app.include_router(auth.router,         prefix="/api/v1/auth",         tags=["Auth"])
# app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
# app.include_router(dashboard.router,    prefix="/api/v1/dashboard",    tags=["Dashboard"])