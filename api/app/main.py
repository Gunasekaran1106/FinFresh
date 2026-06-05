import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exceptions import (
    DuplicateEmailError, InvalidCredentialsError, UserNotFoundError,
    TokenExpiredError, TokenInvalidError, TransactionNotFoundError,
    InvalidObjectIdError, DatabaseError, AppError,
)
from app.database import connect_db, close_db
from app.middleware.error_handler import (
    duplicate_email_handler, invalid_credentials_handler,
    user_not_found_handler, token_expired_handler, token_invalid_handler,
    transaction_not_found_handler, invalid_object_id_handler,
    database_error_handler, app_error_handler,
    validation_exception_handler, unhandled_exception_handler,
)
from app.services.auth_service import ensure_user_indexes
from app.services.transaction_service import ensure_transaction_indexes
from app.routes import auth, transactions, dashboard, financial_health, summary

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up %s v%s …", settings.app_name, settings.app_version)
    await connect_db()
    await ensure_user_indexes()
    await ensure_transaction_indexes()
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
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Exception handlers — order matters: specific before general
# ---------------------------------------------------------------------------
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(DuplicateEmailError,        duplicate_email_handler)
app.add_exception_handler(InvalidCredentialsError,    invalid_credentials_handler)
app.add_exception_handler(UserNotFoundError,          user_not_found_handler)
app.add_exception_handler(TokenExpiredError,          token_expired_handler)
app.add_exception_handler(TokenInvalidError,          token_invalid_handler)
app.add_exception_handler(TransactionNotFoundError,   transaction_not_found_handler)
app.add_exception_handler(InvalidObjectIdError,       invalid_object_id_handler)
app.add_exception_handler(DatabaseError,              database_error_handler)
app.add_exception_handler(AppError,                   app_error_handler)
app.add_exception_handler(Exception,                  unhandled_exception_handler)

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router,              prefix="/api/v1/auth",              tags=["Auth"])
app.include_router(transactions.router,      prefix="/api/v1/transactions",      tags=["Transactions"])
app.include_router(dashboard.router,         prefix="/api/v1/dashboard",         tags=["Dashboard"])
app.include_router(financial_health.router,  prefix="/api/v1",                   tags=["Financial Health"])
app.include_router(summary.router,           prefix="/api/v1",                   tags=["Summary"])