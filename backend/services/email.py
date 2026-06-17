"""
Trust Para Todos — Brevo (Sendinblue) Email Integration.

Sends transactional emails via the Brevo REST API. Uses httpx for async
HTTP calls. All calls are wrapped in try/except with logging.

Template IDs are defined as constants in config.py and referenced here.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from config import settings

logger = logging.getLogger("trust_para_todos.email")

# ---------------------------------------------------------------------------
# Constants — template IDs (loaded from settings; replace in Brevo dashboard)
# ---------------------------------------------------------------------------
TEMPLATE_WELCOME = settings.BREVO_TEMPLATE_WELCOME
TEMPLATE_NOTARY_REMINDER = settings.BREVO_TEMPLATE_NOTARY_REMINDER
TEMPLATE_COURSE_INVITE = settings.BREVO_TEMPLATE_COURSE_INVITE
TEMPLATE_DOCUMENTS_READY = settings.BREVO_TEMPLATE_DOCUMENTS_READY
TEMPLATE_NEXT_STEPS = settings.BREVO_TEMPLATE_NEXT_STEPS
TEMPLATE_INSURANCE_OFFER = settings.BREVO_TEMPLATE_INSURANCE_OFFER
TEMPLATE_LEAD_DAY_0 = settings.BREVO_TEMPLATE_LEAD_DAY_0
TEMPLATE_LEAD_DAY_1 = settings.BREVO_TEMPLATE_LEAD_DAY_1
TEMPLATE_LEAD_DAY_2 = settings.BREVO_TEMPLATE_LEAD_DAY_2
TEMPLATE_LEAD_DAY_3 = settings.BREVO_TEMPLATE_LEAD_DAY_3
TEMPLATE_LEAD_DAY_5 = settings.BREVO_TEMPLATE_LEAD_DAY_5


# ---------------------------------------------------------------------------
# Core API call
# ---------------------------------------------------------------------------
async def send_transactional_email(
    to_email: str,
    template_id: int,
    params: Optional[Dict[str, Any]] = None,
    to_name: Optional[str] = None,
) -> bool:
    """
    Send a transactional email via Brevo's REST API.

    Args:
        to_email: Recipient email address.
        template_id: Brevo transactional template ID (integer).
        params: Template variables to merge (e.g. {"nombre": "Carlos", "panel_link": "..."}).
        to_name: Optional recipient name.

    Returns True on success, False on failure.
    """
    if not settings.is_brevo_configured:
        logger.warning(
            "Brevo no está configurado (placeholder key). "
            "Email a %s (template %d) no enviado — simulando.",
            to_email,
            template_id,
        )
        # Log the would-be email for debugging
        logger.info(
            "📧 [SIMULADO] Para: %s <%s> | Template: %d | Params: %s",
            to_name or "",
            to_email,
            template_id,
            params,
        )
        return True  # Return True so the fulfillment pipeline doesn't break in dev

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.BREVO_API_KEY,
    }

    payload: Dict[str, Any] = {
        "to": [
            {
                "email": to_email,
                **({"name": to_name} if to_name else {}),
            }
        ],
        "templateId": template_id,
        "sender": {
            "email": settings.BREVO_SENDER_EMAIL,
            "name": settings.BREVO_SENDER_NAME,
        },
    }

    if params:
        payload["params"] = params

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.BREVO_API_URL}/smtp/email",
                headers=headers,
                json=payload,
            )

        if response.status_code == 201:
            body = response.json()
            message_id = body.get("messageId", "unknown")
            logger.info(
                "Email transaccional enviado: para=%s template=%d messageId=%s",
                to_email,
                template_id,
                message_id,
            )
            return True
        else:
            logger.error(
                "Brevo API error: status=%d body=%s para=%s template=%d",
                response.status_code,
                response.text,
                to_email,
                template_id,
            )
            return False

    except httpx.TimeoutException:
        logger.error("Brevo API timeout enviando email a %s", to_email)
        return False
    except httpx.ConnectError:
        logger.error("Brevo API connection error enviando email a %s", to_email)
        return False
    except Exception:
        logger.exception("Error inesperado enviando email transaccional a %s", to_email)
        return False


# ---------------------------------------------------------------------------
# Welcome Sequence (Post-Purchase)
# ---------------------------------------------------------------------------
async def send_welcome_sequence(customer_email: str, customer_name: str) -> bool:
    """
    Trigger the first welcome email in the post-purchase sequence.

    The remaining emails in the sequence (day 1, 2, 3, 5, 7) are sent via
    Brevo's automation/workflow feature, triggered by this first email or
    by adding the contact to a list. This function sends only day-0.

    Args:
        customer_email: Customer's email address.
        customer_name: Customer's first name (for personalization).

    Returns True on success, False on failure.
    """
    params = {
        "nombre": customer_name,
        "panel_link": f"{settings.FRONTEND_URL}/panel",
    }

    logger.info("Iniciando secuencia de bienvenida para %s <%s>", customer_name, customer_email)
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_WELCOME,
        params=params,
        to_name=customer_name,
    )


async def send_notary_reminder(customer_email: str, customer_name: str, notary_link: str) -> bool:
    """Send the notary scheduling reminder email (day 1)."""
    params = {
        "nombre": customer_name,
        "notary_link": notary_link,
    }
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_NOTARY_REMINDER,
        params=params,
        to_name=customer_name,
    )


async def send_course_invite(customer_email: str, customer_name: str, course_link: str) -> bool:
    """Send the Trustee 101 course invitation email (day 2)."""
    params = {
        "nombre": customer_name,
        "course_link": course_link,
    }
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_COURSE_INVITE,
        params=params,
        to_name=customer_name,
    )


async def send_documents_ready(
    customer_email: str,
    customer_name: str,
    documents_link: str
) -> bool:
    """Send the documents-ready notification email (day 3)."""
    params = {
        "nombre": customer_name,
        "documents_link": documents_link,
    }
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_DOCUMENTS_READY,
        params=params,
        to_name=customer_name,
    )


async def send_next_steps(customer_email: str, customer_name: str, trustoffice_link: str) -> bool:
    """Send the next-steps email (day 5)."""
    params = {
        "nombre": customer_name,
        "trustoffice_link": trustoffice_link,
    }
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_NEXT_STEPS,
        params=params,
        to_name=customer_name,
    )


async def send_insurance_offer(
    customer_email: str,
    customer_name: str,
    insurance_link: str
) -> bool:
    """Send the life insurance upsell email (day 7)."""
    params = {
        "nombre": customer_name,
        "insurance_link": insurance_link,
    }
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_INSURANCE_OFFER,
        params=params,
        to_name=customer_name,
    )


# ---------------------------------------------------------------------------
# Lead Nurture Sequence (Pre-Purchase)
# ---------------------------------------------------------------------------
async def send_lead_email_day_0(customer_email: str, customer_name: str) -> bool:
    """Send the first lead-nurture email (day 0)."""
    params = {"nombre": customer_name}
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_LEAD_DAY_0,
        params=params,
        to_name=customer_name,
    )


async def send_lead_email_day_1(customer_email: str, customer_name: str, evaluation_link: str) -> bool:
    """Send the lead-nurture email for day 1."""
    params = {"nombre": customer_name, "evaluation_link": evaluation_link}
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_LEAD_DAY_1,
        params=params,
        to_name=customer_name,
    )


async def send_lead_email_day_2(customer_email: str, customer_name: str, evaluation_link: str) -> bool:
    """Send the lead-nurture email for day 2."""
    params = {"nombre": customer_name, "evaluation_link": evaluation_link}
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_LEAD_DAY_2,
        params=params,
        to_name=customer_name,
    )


async def send_lead_email_day_3(customer_email: str, customer_name: str, evaluation_link: str) -> bool:
    """Send the lead-nurture email for day 3."""
    params = {"nombre": customer_name, "evaluation_link": evaluation_link}
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_LEAD_DAY_3,
        params=params,
        to_name=customer_name,
    )


async def send_lead_email_day_5(customer_email: str, customer_name: str, evaluation_link: str) -> bool:
    """Send the lead-nurture email for day 5."""
    params = {"nombre": customer_name, "evaluation_link": evaluation_link}
    return await send_transactional_email(
        to_email=customer_email,
        template_id=TEMPLATE_LEAD_DAY_5,
        params=params,
        to_name=customer_name,
    )


# ---------------------------------------------------------------------------
# Contact form email (for contacto.astro form submissions)
# ---------------------------------------------------------------------------
async def send_contact_notification(
    name: str,
    email: str,
    message: str,
) -> bool:
    """
    Send a contact-form notification to the internal team.

    This uses a plain-text email (no template) via Brevo's SMTP API.
    Falls back to logging if Brevo is not configured.
    """
    if not settings.is_brevo_configured:
        logger.info(
            "📧 [SIMULADO] Contacto de %s <%s>: %s",
            name,
            email,
            message[:200],
        )
        return True

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.BREVO_API_KEY,
    }

    payload = {
        "to": [{"email": settings.BREVO_SENDER_EMAIL, "name": "Equipo Trust Para Todos"}],
        "sender": {"email": settings.BREVO_SENDER_EMAIL, "name": "Formulario Web"},
        "subject": f"Nuevo contacto de {name} <{email}>",
        "htmlContent": f"""
            <h2>Nuevo mensaje del formulario de contacto</h2>
            <p><strong>Nombre:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Mensaje:</strong></p>
            <pre>{message}</pre>
        """,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.BREVO_API_URL}/smtp/email",
                headers=headers,
                json=payload,
            )
        if response.status_code == 201:
            logger.info("Notificación de contacto enviada para %s", email)
            return True
        logger.error(
            "Brevo API error enviando contacto: status=%d body=%s",
            response.status_code,
            response.text,
        )
        return False
    except Exception:
        logger.exception("Error enviando notificación de contacto")
        return False