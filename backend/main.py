"""
Trust Para Todos — FastAPI Application Entry Point.

Run with: uvicorn main:app --reload --port 8000
Or:     python main.py
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import Base, engine
from routes import brevo, checkout, orders, questionnaire, stripe_webhook, auth

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("trust_para_todos.main")


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("🚀 Iniciando %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("   Stripe configurado: %s", settings.is_stripe_configured)
    logger.info("   Brevo configurado: %s", settings.is_brevo_configured)
    logger.info("   CORS origins: %s", settings.cors_origin_list)

    # Ensure generated documents directory exists
    os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)

    # Create tables if they don't exist (for dev / first deploy).
    # In production, use Alembic migrations (init_db.py).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Tablas de base de datos verificadas/creadas")

    yield

    # Shutdown
    logger.info("🛑 Cerrando %s", settings.APP_NAME)
    await engine.dispose()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Trust Para Todos — Spanish-first trust platform for I-10 visa holders.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — allow the frontend origin(s)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(questionnaire.router, prefix="/api", tags=["questionnaire"])
app.include_router(checkout.router, prefix="/api", tags=["checkout"])
app.include_router(orders.router, prefix="/api", tags=["orders"])
app.include_router(stripe_webhook.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(brevo.router, prefix="/api/brevo", tags=["brevo"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint for Railway."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "stripe_configured": settings.is_stripe_configured,
        "brevo_configured": settings.is_brevo_configured,
    }


@app.get("/", tags=["health"])
async def root() -> dict:
    """Root endpoint — redirects to docs."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# ---------------------------------------------------------------------------
# Direct execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=int(os.environ.get("PORT", settings.PORT)),
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )