"""Trust Para Todos — Order Creation Route (combined questionnaire + checkout)."""
from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Customer, Order, OrderStatus, PlanType, QuestionnaireResponse, FulfillmentStep, FulfillmentStepName, FulfillmentStepStatus, Document, DocumentType, DocumentStatus
from services.stripe import create_checkout_session
from services.document_generator import generate_document, DOCUMENT_NAMES
import json
import os
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger("trust_para_todos.routes.orders")

router = APIRouter()

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTPUT_DIR = Path(__file__).parent.parent / "generated_docs"


class OrderCreateRequest(BaseModel):
    settlor_1_full_name: str
    settlor_2_full_name: str = ""
    email: str
    phone: str = ""
    citizenship: str = ""
    marital_status: str = ""
    number_of_children: int = 0
    children_names: str = ""
    has_home: str = ""
    home_value: str = ""
    has_accounts: str = ""
    has_foreign: str = ""
    plan_type: str = "complete"
    affiliate_code: str | None = None


def html_to_pdf(html_content: str, output_path: str) -> str:
    """Convert HTML to PDF using headless Chrome."""
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
        f.write(html_content)
        html_path = f.name
    try:
        subprocess.run(
            [CHROME_PATH, "--headless", f"--print-to-pdf={output_path}",
             "--print-to-pdf-no-header", "--no-margins", f"file://{html_path}"],
            check=True, capture_output=True, timeout=30,
        )
        return output_path
    finally:
        os.unlink(html_path)


@router.post("/orders/create")
async def create_order(data: OrderCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create customer, save questionnaire, create order, generate docs, return checkout URL."""

    # 1. Create or update customer
    result = await db.execute(select(Customer).where(Customer.email == data.email))
    customer = result.scalar_one_or_none()
    if customer is None:
        customer = Customer(
            name=data.settlor_1_full_name,
            email=data.email,
            phone=data.phone or None,
        )
        db.add(customer)
        await db.flush()
    else:
        customer.name = data.settlor_1_full_name
        customer.phone = data.phone or customer.phone

    # 2. Save questionnaire response
    response = QuestionnaireResponse(
        customer_id=customer.id,
        raw_data=data.model_dump(exclude_none=True),
    )
    db.add(response)
    await db.flush()

    # 3. Create order
    plan = PlanType.COMPLETO if data.plan_type == "complete" else PlanType.BASE
    price = 149_700 if plan == PlanType.COMPLETO else 99_700
    order = Order(
        customer_id=customer.id,
        plan_type=plan,
        amount=price,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    await db.flush()

    # 4. Create fulfillment steps
    steps = [
        FulfillmentStep(order_id=order.id, step_name=FulfillmentStepName.PAYMENT_CONFIRMED, status=FulfillmentStepStatus.PENDING),
        FulfillmentStep(order_id=order.id, step_name=FulfillmentStepName.DOCUMENT_GENERATION, status=FulfillmentStepStatus.PENDING),
        FulfillmentStep(order_id=order.id, step_name=FulfillmentStepName.EIN_FILING, status=FulfillmentStepStatus.PENDING),
        FulfillmentStep(order_id=order.id, step_name=FulfillmentStepName.NOTARY_SCHEDULING, status=FulfillmentStepStatus.PENDING),
        FulfillmentStep(order_id=order.id, step_name=FulfillmentStepName.WELCOME_EMAIL, status=FulfillmentStepStatus.PENDING),
        FulfillmentStep(order_id=order.id, step_name=FulfillmentStepName.FINAL_DELIVERY, status=FulfillmentStepStatus.PENDING),
    ]
    for s in steps:
        db.add(s)
    await db.flush()

    # 5. Create Stripe checkout session
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

    order.stripe_session_id = session_id
    await db.commit()

    logger.info("Order created: customer=%s order=%s plan=%s", customer.email, order.id, data.plan_type)

    return {
        "checkout_url": session_url,
        "session_id": session_id,
        "order_id": order.id,
        "customer_id": customer.id,
    }


@router.get("/orders/{order_id}/documents")
async def get_order_documents(order_id: str, db: AsyncSession = Depends(get_db)):
    """Return list of generated documents for an order."""
    result = await db.execute(select(Document).where(Document.order_id == order_id))
    docs = result.scalars().all()
    return [
        {
            "id": d.id,
            "type": d.document_type.value,
            "status": d.status.value,
            "file_path": d.file_path,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ]


@router.get("/orders/{order_id}/documents/{doc_id}/download")
async def download_document(order_id: str, doc_id: int, db: AsyncSession = Depends(get_db)):
    """Download a generated document PDF."""
    result = await db.execute(
        select(Document).where(Document.id == doc_id, Document.order_id == order_id)
    )
    doc = result.scalar_one_or_none()
    if doc is None or not doc.file_path:
        raise HTTPException(status_code=404, detail="Document not found or not ready")

    file_path = Path(doc.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Document file not found on disk")

    from fastapi.responses import FileResponse
    return FileResponse(
        str(file_path),
        media_type="application/pdf",
        filename=file_path.name,
    )


@router.post("/orders/{order_id}/generate-docs")
async def generate_order_documents(order_id: str, db: AsyncSession = Depends(get_db)):
    """Generate all documents for an order (triggered after payment)."""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    cust = await db.get(Customer, order.customer_id)
    if cust is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Build customer data for document generator
    customer_data = {
        "settlor_1_full_name": cust.name,
        "settlor_2_full_name": "",
        "settlor_1_address": "",
        "settlor_1_city": "",
        "governing_state": "California",
        "county_name": "",
        "number_of_children": 0,
        "children_names": "",
        "first_successor_trustee_name": "",
        "first_successor_trustee_address": "",
        "second_successor_trustee_name": "",
        "second_successor_trustee_address": "",
        "executor_name": "",
        "guardian_name": "",
        "guardian_address": "",
        "agent_name": "",
        "healthcare_agent_name": "",
        "trustee_1_full_name": cust.name,
        "trustee_2_full_name": "",
        "grantor_name": cust.name,
        "trustee_name": cust.name,
        "principal_full_name": cust.name,
        "major_decision_threshold": "$10,000",
    }

    # Determine which docs to generate
    doc_types = ["revocable_living_trust"]
    if order.plan_type == PlanType.COMPLETO:
        doc_types = list(DOCUMENT_NAMES.keys())

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = []

    for dt in doc_types:
        try:
            html = generate_document(dt, customer_data)
            doc_name = DOCUMENT_NAMES.get(dt, dt).replace(" ", "_").lower()
            pdf_path = str(OUTPUT_DIR / f"{order_id}_{doc_name}.pdf")
            html_to_pdf(html, pdf_path)

            # Save document record
            doc = Document(
                order_id=order.id,
                document_type=DocumentType(dt),
                status=DocumentStatus.READY,
                file_path=pdf_path,
            )
            db.add(doc)
            generated.append({"type": dt, "path": pdf_path})
        except Exception as e:
            logger.error("Failed to generate %s for order %s: %s", dt, order_id, e)
            doc = Document(
                order_id=order.id,
                document_type=DocumentType(dt),
                status=DocumentStatus.ERROR,
                file_path=None,
            )
            db.add(doc)

    # Update fulfillment steps
    steps_result = await db.execute(
        select(FulfillmentStep).where(
            FulfillmentStep.order_id == order_id,
            FulfillmentStep.step_name == FulfillmentStepName.DOCUMENT_GENERATION,
        )
    )
    step = steps_result.scalar_one_or_none()
    if step:
        step.status = FulfillmentStepStatus.COMPLETED

    await db.commit()

    return {"generated": len(generated), "documents": generated}


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
            "id": d.id,
            "type": d.document_type.value,
            "status": d.status.value,
            "file_path": d.file_path,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "order_id": order_id,
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
