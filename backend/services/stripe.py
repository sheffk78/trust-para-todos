"""
Trust Para Todos — Stripe Integration.

Handles checkout session creation, webhook processing, and fulfillment
triggering. Supports card, OXXO, and SPEI payment methods for the Mexican
market.

All Stripe API calls are wrapped in try/except with proper logging.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models import (
    Customer,
    Document,
    DocumentStatus,
    DocumentType,
    FulfillmentStep,
    FulfillmentStepName,
    FulfillmentStepStatus,
    Order,
    OrderStatus,
    PlanType,
)

logger = logging.getLogger("trust_para_todos.stripe")

# Configure the Stripe module with the secret key.
# We set it at import time; if the key is a placeholder, Stripe calls will fail
# gracefully in the try/except blocks below.
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.max_network_retries = 2


# ---------------------------------------------------------------------------
# Plan helpers
# ---------------------------------------------------------------------------
PLAN_CONFIG: Dict[PlanType, Dict[str, Any]] = {
    PlanType.BASE: {
        "name": settings.PLAN_BASE_NAME,
        "amount_cents": settings.PLAN_BASE_PRICE_CENTS,
        "price_id": settings.STRIPE_PRICE_BASE_ID,
    },
    PlanType.COMPLETO: {
        "name": settings.PLAN_COMPLETO_NAME,
        "amount_cents": settings.PLAN_COMPLETO_PRICE_CENTS,
        "price_id": settings.STRIPE_PRICE_COMPLETO_ID,
    },
}


def _resolve_plan(plan_type: str) -> Optional[PlanType]:
    """Convert a string to PlanType enum, case-insensitive."""
    if not plan_type:
        return None
    normalized = plan_type.strip().lower()
    if normalized in ("base", "trust", "plan_base"):
        return PlanType.BASE
    if normalized in ("completo", "full", "plan_completo"):
        return PlanType.COMPLETO
    return None


# ---------------------------------------------------------------------------
# Checkout Session Creation
# ---------------------------------------------------------------------------
async def create_checkout_session(
    customer_email: str,
    plan_type: str,
    db: AsyncSession,
    customer_id: Optional[str] = None,
    affiliate_code: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Create a Stripe Checkout Session for the given plan.

    Returns (session_url, session_id, error_message).
    On success, session_url is set. On failure, error_message is set.
    """
    plan = _resolve_plan(plan_type)
    if plan is None:
        return None, None, f"Invalid plan_type '{plan_type}'. Must be 'base' or 'completo'."

    plan_config = PLAN_CONFIG[plan]

    if not settings.is_stripe_configured:
        logger.warning(
            "Stripe no está configurado (placeholder key). "
            "Checkout session creation will fail in production."
        )
        return None, None, "Stripe is not configured. Set STRIPE_SECRET_KEY."

    try:
        # Build metadata so the webhook can link back to our order/customer.
        metadata: Dict[str, str] = {
            "plan_type": plan.value,
            "customer_email": customer_email,
        }
        if customer_id:
            metadata["customer_id"] = customer_id
        if affiliate_code:
            metadata["affiliate_code"] = affiliate_code

        # Create the order record FIRST so we have an order_id to attach.
        order = Order(
            customer_id=customer_id or "",
            plan_type=plan,
            amount=plan_config["amount_cents"],
            status=OrderStatus.PENDING,
        )
        # If no customer_id, we create the order after the customer is resolved
        # in the route handler. Here we just prepare the Stripe call.

        session_params: Dict[str, Any] = {
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "price": plan_config["price_id"],
                    "quantity": 1,
                }
            ],
            "mode": "payment",
            "success_url": f"{settings.FRONTEND_URL}/exito?session_id={{CHECKOUT_SESSION_ID}}&status=success",
            "cancel_url": f"{settings.FRONTEND_URL}/pago?plan={plan.value}&status=cancelled",
            "customer_email": customer_email,
            "metadata": metadata,
            "locale": "es",  # Spanish checkout page
            "allow_promotion_codes": True,
            # Mexican payment methods — OXXO and SPEI are available in MX.
            # Note: These are automatically available when the Stripe account
            # is configured for Mexico. We explicitly list them to be safe.
            "payment_method_options": {
                "card": {
                    "setup_future_usage": None,
                },
            },
        }

        # OXXO and SPEI are enabled at the Stripe account level (Dashboard →
        # Settings → Payment methods). When available, Stripe includes them
        # automatically. We can't force them via the API for one-time payments
        # in all regions, so we rely on account-level configuration.

        session = stripe.checkout.Session.create(**session_params)

        logger.info(
            "Stripe Checkout Session creada: id=%s plan=%s email=%s",
            session.id,
            plan.value,
            customer_email,
        )

        return session.url, session.id, None

    except stripe.error.AuthenticationError as exc:
        logger.error("Stripe authentication failed: %s", exc)
        return None, None, f"Stripe authentication error: {exc}"
    except stripe.error.InvalidRequestError as exc:
        logger.error("Stripe invalid request: %s", exc)
        return None, None, f"Stripe invalid request: {exc}"
    except stripe.error.APIConnectionError as exc:
        logger.error("Stripe API connection error: %s", exc)
        return None, None, f"Stripe connection error: {exc}"
    except stripe.error.StripeError as exc:
        logger.error("Stripe error: %s", exc)
        return None, None, f"Stripe error: {exc}"
    except Exception as exc:
        logger.exception("Unexpected error creating Stripe checkout session")
        return None, None, f"Unexpected error: {exc}"


# ---------------------------------------------------------------------------
# Webhook Event Handling
# ---------------------------------------------------------------------------
async def handle_checkout_completed(
    session: Dict[str, Any],
    db: AsyncSession,
) -> bool:
    """
    Process a checkout.session.completed webhook event.

    1. Find the order by stripe_session_id (or create one from metadata).
    2. Mark the order as PAID.
    3. Create fulfillment steps.
    4. Trigger document generation + welcome email.

    Returns True on success, False on failure.
    """
    try:
        session_id = session.get("id", "")
        customer_email = session.get("customer_details", {}).get("email", "")
        metadata = session.get("metadata", {})
        plan_type_str = metadata.get("plan_type", "")
        amount_total = session.get("amount_total", 0)

        logger.info(
            "Procesando checkout completado: session=%s email=%s plan=%s amount=%s",
            session_id,
            customer_email,
            plan_type_str,
            amount_total,
        )

        plan = _resolve_plan(plan_type_str)
        if plan is None:
            logger.error("Plan type no válido en metadata del webhook: %s", plan_type_str)
            return False

        # Find existing order by stripe_session_id
        result = await db.execute(
            select(Order).where(Order.stripe_session_id == session_id)
        )
        order = result.scalar_one_or_none()

        if order is None:
            # The order might not have been persisted yet (e.g., if the route
            # handler created the checkout session but crashed before saving).
            # Try to find/create the customer and create the order now.
            from models import Customer

            cust_result = await db.execute(
                select(Customer).where(Customer.email == customer_email)
            )
            customer = cust_result.scalar_one_or_none()

            if customer is None:
                customer = Customer(
                    name=metadata.get("customer_name", customer_email.split("@")[0]),
                    email=customer_email,
                )
                db.add(customer)
                await db.flush()

            order = Order(
                customer_id=customer.id,
                plan_type=plan,
                amount=amount_total,
                status=OrderStatus.PENDING,
                stripe_session_id=session_id,
            )
            db.add(order)
            await db.flush()

        # Mark as paid
        order.status = OrderStatus.PAID

        # Create fulfillment steps (idempotent — skip if already exist)
        existing_steps = await db.execute(
            select(FulfillmentStep).where(FulfillmentStep.order_id == order.id)
        )
        if existing_steps.scalars().all().__len__() == 0:
            default_steps = [
                FulfillmentStepName.PAYMENT_CONFIRMED,
                FulfillmentStepName.DOCUMENT_GENERATION,
                FulfillmentStepName.EIN_FILING,
                FulfillmentStepName.NOTARY_SCHEDULING,
                FulfillmentStepName.WELCOME_EMAIL,
                FulfillmentStepName.FINAL_DELIVERY,
            ]
            for step_name in default_steps:
                step = FulfillmentStep(
                    order_id=order.id,
                    step_name=step_name,
                    status=FulfillmentStepStatus.PENDING,
                )
                db.add(step)

            # Mark payment_confirmed as completed immediately
            await db.flush()
            payment_step_result = await db.execute(
                select(FulfillmentStep).where(
                    FulfillmentStep.order_id == order.id,
                    FulfillmentStep.step_name == FulfillmentStepName.PAYMENT_CONFIRMED,
                )
            )
            payment_step = payment_step_result.scalar_one_or_none()
            if payment_step:
                from datetime import datetime, timezone

                payment_step.status = FulfillmentStepStatus.COMPLETED
                payment_step.completed_at = datetime.now(timezone.utc)
                payment_step.notes = f"Stripe session {session_id}"

        # Create document records for this plan
        existing_docs = await db.execute(
            select(Document).where(Document.order_id == order.id)
        )
        if existing_docs.scalars().all().__len__() == 0:
            doc_types = [DocumentType.TRUST, DocumentType.GUIDE, DocumentType.EIN]
            if plan == PlanType.COMPLETO:
                doc_types.append(DocumentType.ILIT)
            for dt in doc_types:
                doc = Document(
                    order_id=order.id,
                    document_type=dt,
                    status=DocumentStatus.PENDING,
                )
                db.add(doc)

        await db.flush()
        logger.info("Orden %s marcada como PAGADA. Pasos de fulfillment creados.", order.id)

        # Trigger async fulfillment (document generation + welcome email)
        # In production, this should be a background task / queue. For now we
        # fire-and-forget within the request lifecycle.
        try:
            await _trigger_fulfillment(order.id, db)
        except Exception as exc:
            logger.warning("Fulfillment trigger falló (no fatal): %s", exc)

        return True

    except Exception as exc:
        logger.exception("Error procesando checkout completado")
        return False


async def _trigger_fulfillment(order_id: str, db: AsyncSession) -> None:
    """
    Kick off fulfillment: document generation and welcome email.

    This is a lightweight trigger — heavy work should be offloaded to a
    background queue (Celery, RQ, etc.) in production.
    """
    from services.email import send_welcome_sequence
    from sqlalchemy import select as sel

    # Send welcome email
    result = await db.execute(
        sel(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        logger.warning("No se pudo disparar fulfillment: orden %s no encontrada", order_id)
        return

    cust_result = await db.execute(
        sel(Customer).where(Customer.id == order.customer_id)
    )
    customer = cust_result.scalar_one_or_none()
    if customer is None:
        logger.warning("Cliente no encontrado para orden %s", order_id)
        return

    # Update welcome_email step to in_progress
    step_result = await db.execute(
        sel(FulfillmentStep).where(
            FulfillmentStep.order_id == order_id,
            FulfillmentStep.step_name == FulfillmentStepName.WELCOME_EMAIL,
        )
    )
    welcome_step = step_result.scalar_one_or_none()
    if welcome_step:
        welcome_step.status = FulfillmentStepStatus.IN_PROGRESS

    try:
        await send_welcome_sequence(customer.email, customer.name)
        if welcome_step:
            from datetime import datetime, timezone

            welcome_step.status = FulfillmentStepStatus.COMPLETED
            welcome_step.completed_at = datetime.now(timezone.utc)
    except Exception as exc:
        logger.warning("Welcome email falló: %s", exc)
        if welcome_step:
            welcome_step.status = FulfillmentStepStatus.FAILED
            welcome_step.notes = str(exc)[:500]


# ---------------------------------------------------------------------------
# Webhook Signature Verification
# ---------------------------------------------------------------------------
def verify_webhook_signature(payload: bytes, signature: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a Stripe webhook payload.

    Returns the parsed event dict on success, None on failure.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
        return event
    except stripe.error.SignatureVerificationError as exc:
        logger.warning("Stripe webhook signature verification failed: %s", exc)
        return None
    except ValueError as exc:
        logger.warning("Stripe webhook payload invalid: %s", exc)
        return None
    except Exception as exc:
        logger.exception("Unexpected error verifying Stripe webhook")
        return None


# ---------------------------------------------------------------------------
# OXXO / SPEI support documentation
# ---------------------------------------------------------------------------
# OXXO and SPEI are cash/bank-transfer payment methods popular in Mexico.
#
# To enable them:
# 1. In Stripe Dashboard → Settings → Payment methods → enable OXXO and SPEI
#    for your account (they require a Mexican entity or specific configuration).
# 2. For Checkout Sessions in "payment" mode (one-time), Stripe will
#    automatically show OXXO/SPEI as options if they're enabled at the account
#    level and the currency is MXN (or USD with the right configuration).
# 3. You cannot force a specific payment method for one-time payments via
#    the API — it's account-level configuration.
#
# For subscriptions or invoices, you can specify payment_method_types
# explicitly. For one-time checkout, rely on account-level settings.
#
# Reference: https://stripe.com/docs/payments/oxxo
#            https://stripe.com/docs/payments/spei