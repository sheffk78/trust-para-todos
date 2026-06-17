"""Trust Para Todos — Brevo Email API Route."""
from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from services.email import (
    send_transactional_email,
    send_welcome_sequence,
    send_lead_email_day_0,
    send_contact_notification,
)

logger = logging.getLogger("trust_para_todos.routes.brevo")
router = APIRouter()

class EmailSend(BaseModel):
    to_email: EmailStr
    template_id: int
    to_name: str | None = None
    params: dict | None = None

class LeadNurture(BaseModel):
    email: EmailStr
    name: str
    day: int = 0

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

@router.post("/brevo/send")
async def send_email(data: EmailSend):
    """Send a transactional email via Brevo."""
    success = await send_transactional_email(
        to_email=data.to_email,
        template_id=data.template_id,
        params=data.params or {},
        to_name=data.to_name,
    )
    return {"sent": success}

@router.post("/brevo/lead-nurture")
async def trigger_lead_nurture(data: LeadNurture):
    """Trigger a lead nurture email by day."""
    from config import settings
    evaluation_link = f"{settings.FRONTEND_URL}/evaluacion"
    senders = {
        0: send_lead_email_day_0,
        1: lambda e, n: __import__("services.email", fromlist=["send_lead_email_day_1"]).send_lead_email_day_1(e, n, evaluation_link),
    }
    sender = senders.get(data.day)
    if sender is None:
        raise HTTPException(status_code=400, detail=f"No handler for day {data.day}")
    success = await sender(data.email, data.name)
    return {"sent": success}

@router.post("/brevo/contact")
async def contact_form(data: ContactForm):
    """Send a contact form notification to the team."""
    success = await send_contact_notification(name=data.name, email=data.email, message=data.message)
    return {"sent": success}