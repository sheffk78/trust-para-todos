"""Trust Para Todos — Order Status Routes."""
from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Order, Customer, FulfillmentStep, Document

logger = logging.getLogger("trust_para_todos.routes.orders")
router = APIRouter()

@router.get("/orders/{order_id}/status")
async def get_order_status(order_id: str, db: AsyncSession = Depends(get_db)):
    """Return full fulfillment status for an order."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    cust = await db.get(Customer, order.customer_id)

    steps_result = await db.execute(
        select(FulfillmentStep).where(FulfillmentStep.order_id == order_id).order_by(FulfillmentStep.created_at)
    )
    steps = [
        {
            "name": s.step_name.value,
            "status": s.status.value,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "notes": s.notes,
        }
        for s in steps_result.scalars().all()
    ]

    docs_result = await db.execute(
        select(Document).where(Document.order_id == order_id)
    )
    docs = [
        {
            "type": d.document_type.value,
            "status": d.status.value,
            "file_path": d.file_path,
        }
        for d in docs_result.scalars().all()
    ]

    return {
        "order_id": order.id,
        "customer_name": cust.name if cust else "",
        "plan_type": order.plan_type.value,
        "amount": order.amount,
        "status": order.status.value,
        "created_at": order.created_at.isoformat(),
        "steps": steps,
        "documents": docs,
    }

@router.get("/orders/by-email/{email}")
async def get_orders_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """Return all orders for a given email."""
    result = await db.execute(select(Customer).where(Customer.email == email))
    customer = result.scalar_one_or_none()
    if customer is None:
        # Return empty, not 404 — the customer might not have purchased yet
        return {"customer": None, "orders": []}

    orders_result = await db.execute(
        select(Order).where(Order.customer_id == customer.id).order_by(Order.created_at.desc())
    )
    orders = [
        {
            "id": o.id,
            "plan_type": o.plan_type.value,
            "status": o.status.value,
            "created_at": o.created_at.isoformat(),
        }
        for o in orders_result.scalars().all()
    ]

    return {
        "customer": {"id": customer.id, "name": customer.name, "email": customer.email},
        "orders": orders,
    }