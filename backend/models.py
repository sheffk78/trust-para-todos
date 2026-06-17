"""
Trust Para Todos — SQLAlchemy ORM Models.

All models use async-compatible SQLAlchemy 2.0 style (Mapped / mapped_column).
Enums are stored as native PostgreSQL ENUMs when on Postgres, or VARCHAR on SQLite.
"""

from __future__ import annotations

import enum
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

logger = logging.getLogger("trust_para_todos.models")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _generate_uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class PlanType(str, enum.Enum):
    """Product tiers offered."""
    BASE = "base"        # Trust Para Todos — $997
    COMPLETO = "completo"  # Trust + ILIT — $1,494


class OrderStatus(str, enum.Enum):
    """Lifecycle of an order."""
    PENDING = "pending"        # Created, awaiting payment
    PAID = "paid"              # Payment confirmed via Stripe webhook
    FULFILLING = "fulfilling"   # Documents being generated / notary being scheduled
    COMPLETE = "complete"      # All deliverables ready


class DocumentType(str, enum.Enum):
    """Types of documents the system generates."""
    TRUST = "trust"    # Revocable living trust
    ILIT = "ilit"      # Irrevocable Life Insurance Trust
    EIN = "ein"        # EIN application / confirmation
    GUIDE = "guide"    # Spanish explanatory guide


class DocumentStatus(str, enum.Enum):
    """Status of a single document."""
    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    ERROR = "error"


class FulfillmentStepName(str, enum.Enum):
    """Named steps in the fulfillment pipeline."""
    PAYMENT_CONFIRMED = "payment_confirmed"
    DOCUMENT_GENERATION = "document_generation"
    EIN_FILING = "ein_filing"
    NOTARY_SCHEDULING = "notary_scheduling"
    WELCOME_EMAIL = "welcome_email"
    FINAL_DELIVERY = "final_delivery"


class FulfillmentStepStatus(str, enum.Enum):
    """Status of a single fulfillment step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class Customer(Base):
    """A person who has started the questionnaire or placed an order."""

    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    visa_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # Relationships
    orders: Mapped[List["Order"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    questionnaire_responses: Mapped[List["QuestionnaireResponse"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Customer {self.email}>"


class Order(Base):
    """A purchase: either BASE or COMPLETO plan."""

    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_generate_uuid)
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_type: Mapped[PlanType] = mapped_column(
        Enum(PlanType, native_enum=False), nullable=False
    )
    amount: Mapped[int] = mapped_column(nullable=False)  # in cents
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False),
        nullable=False,
        default=OrderStatus.PENDING,
        index=True,
    )
    stripe_session_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    documents: Mapped[List["Document"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    fulfillment_steps: Mapped[List["FulfillmentStep"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Order {self.id} {self.plan_type.value} {self.status.value}>"


class QuestionnaireResponse(Base):
    """Raw JSON response from the evaluation form (StatusCheck.tsx)."""

    __tablename__ = "questionnaire_responses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_generate_uuid)
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    raw_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="questionnaire_responses")

    def __repr__(self) -> str:
        return f"<QuestionnaireResponse {self.customer_id}>"


class Document(Base):
    """A generated legal document (trust, ILIT, EIN, or guide)."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_generate_uuid)
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, native_enum=False), nullable=False
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, native_enum=False),
        nullable=False,
        default=DocumentStatus.PENDING,
    )
    file_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document {self.document_type.value} {self.status.value}>"


class FulfillmentStep(Base):
    """A single step in the order fulfillment pipeline."""

    __tablename__ = "fulfillment_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_generate_uuid)
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step_name: Mapped[FulfillmentStepName] = mapped_column(
        Enum(FulfillmentStepName, native_enum=False), nullable=False
    )
    status: Mapped[FulfillmentStepStatus] = mapped_column(
        Enum(FulfillmentStepStatus, native_enum=False),
        nullable=False,
        default=FulfillmentStepStatus.PENDING,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="fulfillment_steps")

    def __repr__(self) -> str:
        return f"<FulfillmentStep {self.step_name.value} {self.status.value}>"