"""Trust Para Todos — Questionnaire Routes."""
from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Customer, QuestionnaireResponse

logger = logging.getLogger("trust_para_todos.routes.questionnaire")
router = APIRouter()

class QuestionnaireSubmit(BaseModel):
    nombre: str
    email: EmailStr
    telefono: str | None = None
    visa: str | None = None
    residencia: str | None = None
    domicilio: str | None = None
    estado_civil: str | None = None
    conyuge_ciudadano: str | None = None
    hijos: str | None = None
    casa: str | None = None
    estado_propiedad: str | None = None
    valor: str | None = None
    codigo_afiliado: str | None = None

@router.post("/questionnaire")
async def submit_questionnaire(data: QuestionnaireSubmit, db: AsyncSession = Depends(get_db)):
    """Receive the 5-step evaluation form, create/update customer, save response."""
    result = await db.execute(select(Customer).where(Customer.email == data.email))
    customer = result.scalar_one_or_none()
    if customer is None:
        customer = Customer(name=data.nombre, email=data.email)
        db.add(customer)
        await db.flush()
    else:
        customer.name = data.nombre
        customer.phone = data.telefono or customer.phone
        customer.visa_type = data.visa or customer.visa_type

    response = QuestionnaireResponse(
        customer_id=customer.id,
        raw_data=data.model_dump(exclude_none=True),
    )
    db.add(response)
    await db.flush()
    logger.info("Cuestionario guardado: customer=%s id=%s", customer.email, response.id)
    return {"status": "ok", "customer_id": customer.id, "response_id": response.id}