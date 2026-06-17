"""
Trust Para Todos — Document Generation Engine.

Generates legal documents (trust, ILIT, EIN, guide) from Jinja2 templates
and renders them to PDF using WeasyPrint.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import settings

logger = logging.getLogger("trust_para_todos.documents")

# ---------------------------------------------------------------------------
# Jinja2 environment — loads templates from backend/templates/
# ---------------------------------------------------------------------------
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"

jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


# ---------------------------------------------------------------------------
# PDF rendering
# ---------------------------------------------------------------------------
def render_to_pdf(html_content: str, output_path: str) -> bool:
    """
    Convert HTML content to a PDF file using WeasyPrint.

    Args:
        html_content: Full HTML string to render.
        output_path: Absolute or relative path where the PDF will be saved.

    Returns True on success, False on failure.
    """
    try:
        # WeasyPrint is imported lazily so the service can load even if
        # system deps (cairo, pango) aren't installed during development.
        from weasyprint import HTML

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        HTML(string=html_content).write_pdf(output_path)

        logger.info("PDF generado: %s", output_path)
        return True

    except ImportError:
        logger.error(
            "WeasyPrint no está instalado o faltan dependencias del sistema "
            "(cairo, pango, gdk-pixbuf). Instala con: pip install weasyprint "
            "y asegúrate de tener las librerías del sistema."
        )
        return False
    except Exception:
        logger.exception("Error generando PDF en %s", output_path)
        return False


# ---------------------------------------------------------------------------
# Trust Document Generation
# ---------------------------------------------------------------------------
def generate_trust_document(customer_data: Dict[str, Any]) -> str:
    """
    Build a personalized revocable living trust document from the Jinja2 template.

    Args:
        customer_data: Dict with keys:
            - customer_name (str, required)
            - spouse_name (str, optional)
            - property_address (str, optional)
            - beneficiaries (list[str], optional)
            - trustee_name (str, optional — defaults to customer_name)
            - date (str, optional — defaults to today)
            - state (str, optional — e.g. "California")
            - email (str, optional)
            - phone (str, optional)

    Returns:
        Rendered HTML string.
    """
    try:
        template = jinja_env.get_template("trust_document.html")

        # Prepare context with sensible defaults
        now = datetime.now(timezone.utc)
        context: Dict[str, Any] = {
            "customer_name": customer_data.get("customer_name", "[NOMBRE DEL FIRMANTE]"),
            "spouse_name": customer_data.get("spouse_name", ""),
            "property_address": customer_data.get("property_address", "[DIRECCIÓN DE LA PROPIEDAD]"),
            "beneficiaries": customer_data.get("beneficiaries", ["[BENEFICIARIO 1]"]),
            "trustee_name": customer_data.get("trustee_name", customer_data.get("customer_name", "[NOMBRE DEL TRUSTEE]")),
            "successor_trustee_name": customer_data.get(
                "successor_trustee_name", "[NOMBRE DEL TRUSTEE SUCESOR]"
            ),
            "date": customer_data.get("date", now.strftime("%d de %B de %Y")),
            "state": customer_data.get("state", "[ESTADO]"),
            "email": customer_data.get("email", ""),
            "phone": customer_data.get("phone", ""),
            "year": now.year,
        }

        html = template.render(**context)
        logger.info("Documento de trust generado para: %s", context["customer_name"])
        return html

    except Exception:
        logger.exception("Error generando documento de trust")
        raise


# ---------------------------------------------------------------------------
# ILIT Document Generation
# ---------------------------------------------------------------------------
def generate_ilit_document(customer_data: Dict[str, Any]) -> str:
    """
    Build a personalized Irrevocable Life Insurance Trust (ILIT) document.

    Uses a simpler inline template since ILITs are an add-on.
    """
    try:
        template = jinja_env.get_template("ilit_document.html")
        now = datetime.now(timezone.utc)

        context: Dict[str, Any] = {
            "customer_name": customer_data.get("customer_name", "[NOMBRE DEL FIDEICOMITENTE]"),
            "trustee_name": customer_data.get("trustee_name", customer_data.get("customer_name", "[NOMBRE DEL TRUSTEE]")),
            "beneficiaries": customer_data.get("beneficiaries", ["[BENEFICIARIO 1]"]),
            "date": customer_data.get("date", now.strftime("%d de %B de %Y")),
            "state": customer_data.get("state", "[ESTADO]"),
            "year": now.year,
        }

        html = template.render(**context)
        logger.info("Documento ILIT generado para: %s", context["customer_name"])
        return html
    except Exception:
        logger.exception("Error generando documento ILIT")
        raise


# ---------------------------------------------------------------------------
# EIN Guide / Application
# ---------------------------------------------------------------------------
def generate_ein_document(customer_data: Dict[str, Any]) -> str:
    """
    Generate the EIN application summary and instructions (Spanish).
    """
    try:
        template = jinja_env.get_template("ein_document.html")
        now = datetime.now(timezone.utc)

        context: Dict[str, Any] = {
            "customer_name": customer_data.get("customer_name", "[NOMBRE]"),
            "trust_name": customer_data.get("trust_name", f"Trust {customer_data.get('customer_name', '[NOMBRE]')}"),
            "date": customer_data.get("date", now.strftime("%d de %B de %Y")),
            "year": now.year,
        }

        html = template.render(**context)
        logger.info("Documento EIN generado para: %s", context["customer_name"])
        return html
    except Exception:
        logger.exception("Error generando documento EIN")
        raise


# ---------------------------------------------------------------------------
# Explanatory Guide
# ---------------------------------------------------------------------------
def generate_guide_document(customer_data: Dict[str, Any]) -> str:
    """
    Generate the Spanish explanatory guide for the customer's trust.
    """
    try:
        template = jinja_env.get_template("guide_document.html")
        now = datetime.now(timezone.utc)

        context: Dict[str, Any] = {
            "customer_name": customer_data.get("customer_name", "[NOMBRE]"),
            "date": customer_data.get("date", now.strftime("%d de %B de %Y")),
            "year": now.year,
        }

        html = template.render(**context)
        logger.info("Guía explicativa generada para: %s", context["customer_name"])
        return html
    except Exception:
        logger.exception("Error generando guía")
        raise


# ---------------------------------------------------------------------------
# Full pipeline: generate a document and save as PDF
# ---------------------------------------------------------------------------
def generate_and_save_pdf(
    customer_data: Dict[str, Any],
    document_type: str,
    order_id: str,
) -> Optional[str]:
    """
    Generate a document of the given type and save it as a PDF.

    Args:
        customer_data: Customer + questionnaire data.
        document_type: "trust", "ilit", "ein", or "guide".
        order_id: Used to construct the output file path.

    Returns the file path on success, None on failure.
    """
    generators = {
        "trust": generate_trust_document,
        "ilit": generate_ilit_document,
        "ein": generate_ein_document,
        "guide": generate_guide_document,
    }

    generator = generators.get(document_type)
    if generator is None:
        logger.error("Tipo de documento no válido: %s", document_type)
        return None

    try:
        html = generator(customer_data)

        # Build output path: DOCUMENTS_DIR/{order_id}/{document_type}.pdf
        output_dir = Path(settings.DOCUMENTS_DIR) / order_id
        output_path = str(output_dir / f"{document_type}.pdf")

        success = render_to_pdf(html, output_path)
        if success:
            return output_path
        return None

    except Exception:
        logger.exception("Error en generate_and_save_pdf para tipo=%s", document_type)
        return None