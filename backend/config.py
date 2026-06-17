"""
Trust Para Todos — Application Configuration.

Loads all environment variables with sensible defaults for local development.
In production (Railway), these are injected as service variables.
"""

from __future__ import annotations

import logging
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------------
# Logging bootstrap — configured once at import time.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("trust_para_todos")
logger.info("Configuración inicializando…")


class Settings(BaseSettings):
    """Strongly-typed settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- App ----
    APP_NAME: str = "Trust Para Todos API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ---- Database ----
    # Railway injects DATABASE_URL automatically when a Postgres service is linked.
    # Local fallback uses a file-based SQLite for quick onboarding.
    DATABASE_URL: str = "sqlite+aiosqlite:///./trust_para_todos.db"

    # ---- Stripe ----
    # In test mode use sk_test_… ; in production use sk_live_…
    STRIPE_SECRET_KEY: str = "sk_test_placeholder_replace_me"
    STRIPE_WEBHOOK_SECRET: str = "whsec_placeholder_replace_me"
    STRIPE_PRICE_BASE_ID: str = "price_placeholder_base"
    STRIPE_PRICE_COMPLETO_ID: str = "price_placeholder_completo"

    # ---- Brevo (Sendinblue) ----
    BREVO_API_KEY: str = "brevo_placeholder_replace_me"
    BREVO_API_URL: str = "https://api.brevo.com/v3"
    BREVO_SENDER_EMAIL: str = "hola@trustparatodos.com"
    BREVO_SENDER_NAME: str = "Trust Para Todos"

    # Brevo transactional template IDs — replace with real IDs from Brevo dashboard.
    BREVO_TEMPLATE_WELCOME: int = 1
    BREVO_TEMPLATE_NOTARY_REMINDER: int = 2
    BREVO_TEMPLATE_COURSE_INVITE: int = 3
    BREVO_TEMPLATE_DOCUMENTS_READY: int = 4
    BREVO_TEMPLATE_NEXT_STEPS: int = 5
    BREVO_TEMPLATE_INSURANCE_OFFER: int = 6
    BREVO_TEMPLATE_LEAD_DAY_0: int = 7
    BREVO_TEMPLATE_LEAD_DAY_1: int = 8
    BREVO_TEMPLATE_LEAD_DAY_2: int = 9
    BREVO_TEMPLATE_LEAD_DAY_3: int = 10
    BREVO_TEMPLATE_LEAD_DAY_5: int = 11

    # ---- Frontend / CORS ----
    # Comma-separated list of allowed origins.
    FRONTEND_URL: str = "http://localhost:4321"
    CORS_ORIGINS: str = (
        "http://localhost:4321,"
        "http://localhost:3000,"
        "https://trust-para-todos-production.up.railway.app,"
        "https://trustparatodos.com,"
        "https://www.trustparatodos.com"
    )

    # ---- Auth (stub) ----
    AUTH_SECRET: str = "change-me-in-production"
    AUTH_CODE_TTL_SECONDS: int = 600  # 10 minutes

    # ---- Pricing (mirror of frontend; kept in sync for validation) ----
    PLAN_BASE_PRICE_CENTS: int = 99_700   # $997.00
    PLAN_COMPLETO_PRICE_CENTS: int = 149_400  # $1,494.00
    PLAN_BASE_NAME: str = "Trust Para Todos"
    PLAN_COMPLETO_NAME: str = "Paquete Completo (Trust + ILIT)"

    # ---- File storage ----
    # Where generated PDFs are saved. In production use a persistent volume mount.
    DOCUMENTS_DIR: str = "./generated_documents"

    @property
    def cors_origin_list(self) -> List[str]:
        """Parse CORS_ORIGINS into a list, stripping whitespace."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_stripe_configured(self) -> bool:
        """True when a real (non-placeholder) Stripe key is present."""
        return "placeholder" not in self.STRIPE_SECRET_KEY

    @property
    def is_brevo_configured(self) -> bool:
        """True when a real (non-placeholder) Brevo key is present."""
        return "placeholder" not in self.BREVO_API_KEY


# Singleton — import this everywhere.
settings = Settings()

logger.info(
    "Config cargada — Stripe: %s | Brevo: %s | DB: %s",
    "✅" if settings.is_stripe_configured else "⚠️ placeholder",
    "✅" if settings.is_brevo_configured else "⚠️ placeholder",
    settings.DATABASE_URL.split("://")[0] if "://" in settings.DATABASE_URL else "sqlite",
)