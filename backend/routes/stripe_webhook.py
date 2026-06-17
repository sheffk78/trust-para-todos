"""Trust Para Todos — Stripe Webhook Route."""
from __future__ import annotations
import logging
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db_context
from services.stripe import verify_webhook_signature, handle_checkout_completed

logger = logging.getLogger("trust_para_todos.routes.webhook")
router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request):
    """Handle incoming Stripe webhook events."""
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    event = verify_webhook_signature(payload, signature)
    if event is None:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event.get("type", "")
    logger.info("Stripe webhook recibido: %s", event_type)

    if event_type == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        async with get_db_context() as db:
            success = await handle_checkout_completed(session, db)
            if not success:
                logger.error("Fallo al procesar checkout.session.completed")
                return {"received": True, "processed": False}
            logger.info("Checkout session procesada exitosamente")
    else:
        logger.info("Evento webhook ignorado (sin handler): %s", event_type)

    return {"received": True}