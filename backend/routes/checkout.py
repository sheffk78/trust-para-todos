"""Trust Para Todos — Checkout Routes."""
from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Customer, Order, OrderStatus, PlanType
from services.stripe import create_checkout_session

logger = logging.getLogger("trust_para_todos.routes.checkout")
router = APIRouter()

class CheckoutCreate(BaseModel):
    email: EmailStr
    plan_type: str = "base"
    customer_id: str | None = None
    affiliate_code: str | None = None

@router.post("/checkout")
async def create_checkout(data: CheckoutCreate, db: AsyncSession = Depends(get_db)):
    """Create a Stripe checkout session for the given plan."""
    # Resolve customer
    result = await db.execute(select(Customer).where(Customer.email == data.email))
    customer = result.scalar_one_or_none()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found. Submit questionnaire first.")

    # Create order record
    plan = PlanType.BASE if data.plan_type == "base" else PlanType.COMPLETO
    price = 99_700 if plan == PlanType.BASE else 149_400
    order = Order(
        customer_id=customer.id,
        plan_type=plan,
        amount=price,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    await db.flush()

    # Create Stripe session
    session_url, session_id, error = await create_checkout_session(
        customer_email=customer.email,
        plan_type=data.plan_type,
        db=db,
        customer_id=customer.id,
        affiliate_code=data.affiliate_code,
    )
    if error:
        await db.rollback()
        raise HTTPException(status_code=400, detail=error)

    # Link session to order
    order.stripe_session_id = session_id
    await db.flush()

    return {
        "url": session_url,
        "session_id": session_id,
        "order_id": order.id,
    }