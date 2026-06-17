"""
Document Generator Service — Trust Para Todos
Generates personalized legal documents from HTML templates with Jinja2.
"""

import os
import re
from datetime import date
from typing import Dict, Any, Optional
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Map of document types to template files
DOCUMENT_TEMPLATES = {
    "revocable_living_trust": "trust_document.html",
    "pour_over_will": "pour_over_will.html",
    "certificate_of_trust": "certificate_of_trust.html",
    "assignment_of_property": "assignment_of_property.html",
    "durable_power_of_attorney": "durable_power_of_attorney.html",
    "advance_healthcare_directive": "advance_healthcare_directive.html",
}

DOCUMENT_NAMES = {
    "revocable_living_trust": "Revocable Living Trust",
    "pour_over_will": "Pour-Over Will",
    "certificate_of_trust": "Certificate of Trust",
    "assignment_of_property": "Assignment of Personal Property to Trust",
    "durable_power_of_attorney": "Durable Power of Attorney (Financial)",
    "advance_healthcare_directive": "Advance Healthcare Directive",
}


def get_default_placeholders(customer: Dict[str, Any]) -> Dict[str, str]:
    """Build default placeholder values from customer data."""
    settlor_1_name = customer.get("settlor_1_full_name", "")
    settlor_2_name = customer.get("settlor_2_full_name", "")
    settlor_1_first = settlor_1_name.split(" ")[0] if settlor_1_name else ""
    settlor_2_first = settlor_2_name.split(" ")[0] if settlor_2_name else ""
    settlor_1_last = settlor_1_name.split(" ")[-1] if settlor_1_name else ""
    settlor_2_last = settlor_2_name.split(" ")[-1] if settlor_2_name else ""

    return {
        # Trust info
        "trust_name": customer.get("trust_name", f"The {settlor_1_name} and {settlor_2_name} Revocable Living Trust"),
        "trust_date": customer.get("trust_date", date.today().strftime("%B %d, %Y")),
        "file_number": customer.get("file_number", f"TPT-{date.today().strftime('%Y%m')}-{customer.get('id', 'XXXX')}"),

        # Settlors
        "settlor_1_full_name": settlor_1_name,
        "settlor_2_full_name": settlor_2_name,
        "settlor_1_first_name": settlor_1_first,
        "settlor_2_first_name": settlor_2_first,
        "settlor_1_last_name": settlor_1_last,
        "settlor_2_last_name": settlor_2_last,
        "spouse_full_name": settlor_2_name,

        # Addresses
        "settlor_1_address": customer.get("settlor_1_address", ""),
        "settlor_1_city": customer.get("settlor_1_city", ""),
        "settlor_1_state": customer.get("settlor_1_state", ""),

        # Governing law
        "governing_state": customer.get("governing_state", "California"),
        "county_name": customer.get("county_name", ""),

        # Children
        "number_of_children": str(customer.get("number_of_children", 0)),
        "children_names": customer.get("children_names", ""),

        # Preparer
        "preparer_address": customer.get("preparer_address", "Trust Para Todos"),
        "preparer_phone": customer.get("preparer_phone", ""),
        "preparer_email": customer.get("preparer_email", "info@trustparatodos.com"),

        # Trustees
        "first_successor_trustee_name": customer.get("first_successor_trustee_name", ""),
        "first_successor_trustee_address": customer.get("first_successor_trustee_address", ""),
        "second_successor_trustee_name": customer.get("second_successor_trustee_name", ""),
        "second_successor_trustee_address": customer.get("second_successor_trustee_address", ""),
        "third_successor_trustee_name": customer.get("third_successor_trustee_name", ""),
        "third_successor_trustee_address": customer.get("third_successor_trustee_address", ""),

        # Major decision threshold
        "major_decision_threshold": customer.get("major_decision_threshold", "$10,000"),

        # Real property
        "primary_residence_address": customer.get("primary_residence_address", ""),
        "primary_residence_value": customer.get("primary_residence_value", ""),
        "additional_real_property_1_description": customer.get("additional_real_property_1_description", ""),
        "additional_real_property_1_address": customer.get("additional_real_property_1_address", ""),
        "additional_real_property_1_value": customer.get("additional_real_property_1_value", ""),

        # Financial accounts
        "checking_institution": customer.get("checking_institution", ""),
        "checking_value": customer.get("checking_value", ""),
        "savings_institution": customer.get("savings_institution", ""),
        "savings_value": customer.get("savings_value", ""),
        "additional_account_1_type": customer.get("additional_account_1_type", ""),
        "additional_account_1_institution": customer.get("additional_account_1_institution", ""),
        "additional_account_1_value": customer.get("additional_account_1_value", ""),

        # Vehicles
        "vehicle_1_make_model_year": customer.get("vehicle_1_make_model_year", ""),
        "vehicle_1_vin": customer.get("vehicle_1_vin", ""),
        "vehicle_1_value": customer.get("vehicle_1_value", ""),
        "vehicle_2_make_model_year": customer.get("vehicle_2_make_model_year", ""),
        "vehicle_2_vin": customer.get("vehicle_2_vin", ""),
        "vehicle_2_value": customer.get("vehicle_2_value", ""),

        # Household
        "household_value": customer.get("household_value", ""),

        # Other assets
        "other_asset_1_description": customer.get("other_asset_1_description", ""),
        "other_asset_1_details": customer.get("other_asset_1_details", ""),
        "other_asset_1_value": customer.get("other_asset_1_value", ""),
        "other_asset_2_description": customer.get("other_asset_2_description", ""),
        "other_asset_2_details": customer.get("other_asset_2_details", ""),
        "other_asset_2_value": customer.get("other_asset_2_value", ""),

        # Separate property
        "settlor_1_separate_property_1_description": customer.get("settlor_1_separate_property_1_description", ""),
        "settlor_1_separate_property_1_details": customer.get("settlor_1_separate_property_1_details", ""),
        "settlor_1_separate_property_1_value": customer.get("settlor_1_separate_property_1_value", ""),
        "settlor_1_separate_property_2_description": customer.get("settlor_1_separate_property_2_description", ""),
        "settlor_1_separate_property_2_details": customer.get("settlor_1_separate_property_2_details", ""),
        "settlor_1_separate_property_2_value": customer.get("settlor_1_separate_property_2_value", ""),
        "settlor_2_separate_property_1_description": customer.get("settlor_2_separate_property_1_description", ""),
        "settlor_2_separate_property_1_details": customer.get("settlor_2_separate_property_1_details", ""),
        "settlor_2_separate_property_1_value": customer.get("settlor_2_separate_property_1_value", ""),
        "settlor_2_separate_property_2_description": customer.get("settlor_2_separate_property_2_description", ""),
        "settlor_2_separate_property_2_details": customer.get("settlor_2_separate_property_2_details", ""),
        "settlor_2_separate_property_2_value": customer.get("settlor_2_separate_property_2_value", ""),

        # Alternate beneficiaries
        "alternate_beneficiary": customer.get("alternate_beneficiary", "charitable organizations"),

        # Will-specific
        "will_date": customer.get("will_date", date.today().strftime("%B %d, %Y")),
        "executor_name": customer.get("executor_name", settlor_2_name),
        "executor_address": customer.get("executor_address", ""),
        "alternate_executor_name": customer.get("alternate_executor_name", ""),
        "alternate_executor_address": customer.get("alternate_executor_address", ""),
        "specific_bequest_1": customer.get("specific_bequest_1", "None"),
        "specific_bequest_2": customer.get("specific_bequest_2", "None"),
        "specific_bequest_3": customer.get("specific_bequest_3", "None"),
        "guardian_name": customer.get("guardian_name", ""),
        "guardian_address": customer.get("guardian_address", ""),
        "alternate_guardian_name": customer.get("alternate_guardian_name", ""),
        "alternate_guardian_address": customer.get("alternate_guardian_address", ""),

        # Certificate of Trust
        "trustee_1_full_name": customer.get("trustee_1_full_name", settlor_1_name),
        "trustee_2_full_name": customer.get("trustee_2_full_name", settlor_2_name),
        "revocability_status": customer.get("revocability_status", "Revocable during the joint lifetimes of the Settlors; irrevocable upon the death of a Settlor as to that Settlor's property"),
        "trust_tax_id": customer.get("trust_tax_id", ""),
        "manner_of_holding_title": customer.get("manner_of_holding_title", "In the name of the Trustee(s) as Trustee(s) of the Trust"),

        # Assignment
        "grantor_name": customer.get("grantor_name", settlor_1_name),
        "trustee_name": customer.get("trustee_name", settlor_1_name),
        "governing_law_state": customer.get("governing_law_state", "California"),
        "notary_state": customer.get("notary_state", "California"),

        # DPOA
        "dpoa_date": customer.get("dpoa_date", date.today().strftime("%B %d, %Y")),
        "principal_full_name": customer.get("principal_full_name", settlor_1_name),
        "principal_city": customer.get("principal_city", ""),
        "agent_name": customer.get("agent_name", settlor_2_name),
        "agent_address": customer.get("agent_address", ""),
        "agent_phone": customer.get("agent_phone", ""),
        "first_successor_agent_name": customer.get("first_successor_agent_name", ""),
        "first_successor_agent_address": customer.get("first_successor_agent_address", ""),
        "first_successor_agent_phone": customer.get("first_successor_agent_phone", ""),
        "second_successor_agent_name": customer.get("second_successor_agent_name", ""),
        "second_successor_agent_address": customer.get("second_successor_agent_address", ""),
        "second_successor_agent_phone": customer.get("second_successor_agent_phone", ""),

        # AHCD
        "ahcd_date": customer.get("ahcd_date", date.today().strftime("%B %d, %Y")),
        "healthcare_agent_name": customer.get("healthcare_agent_name", settlor_2_name),
        "healthcare_agent_address": customer.get("healthcare_agent_address", ""),
        "healthcare_agent_phone": customer.get("healthcare_agent_phone", ""),
        "alternate_agent_name": customer.get("alternate_agent_name", ""),
        "alternate_agent_address": customer.get("alternate_agent_address", ""),
        "alternate_agent_phone": customer.get("alternate_agent_phone", ""),
        "second_alternate_agent_name": customer.get("second_alternate_agent_name", ""),
        "second_alternate_agent_address": customer.get("second_alternate_agent_address", ""),
        "second_alternate_agent_phone": customer.get("second_alternate_agent_phone", ""),
        "additional_values_statement": customer.get("additional_values_statement", "I wish to be treated in accordance with my cultural and religious traditions."),
        "specific_organs_for_donation": customer.get("specific_organs_for_donation", "any needed organs and tissues"),
        "disposition_method": customer.get("disposition_method", "burial"),
        "disposition_location": customer.get("disposition_location", ""),
        "additional_disposition_instructions": customer.get("additional_disposition_instructions", ""),
        "primary_physician_name": customer.get("primary_physician_name", ""),
        "primary_physician_address": customer.get("primary_physician_address", ""),
        "primary_physician_phone": customer.get("primary_physician_phone", ""),
        "notification_person_1_name": customer.get("notification_person_1_name", ""),
        "notification_person_1_relationship": customer.get("notification_person_1_relationship", ""),
        "notification_person_1_phone": customer.get("notification_person_1_phone", ""),
        "notification_person_2_name": customer.get("notification_person_2_name", ""),
        "notification_person_2_relationship": customer.get("notification_person_2_relationship", ""),
        "notification_person_2_phone": customer.get("notification_person_2_phone", ""),
        "additional_limitation": customer.get("additional_limitation", "None."),
    }


def render_template(template_name: str, placeholders: Dict[str, str]) -> str:
    """Render an HTML template by replacing {{placeholder}} values."""
    template_path = TEMPLATES_DIR / template_name

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    html = template_path.read_text(encoding="utf-8")

    # Replace all {{placeholder}} values
    def replace_placeholder(match):
        key = match.group(1).strip()
        return placeholders.get(key, f"{{{{{key}}}}}")  # Leave unfilled placeholders as-is

    html = re.sub(r"\{\{(\w+)\}\}", replace_placeholder, html)

    return html


def generate_document(
    doc_type: str,
    customer: Dict[str, Any],
    extra_placeholders: Optional[Dict[str, str]] = None,
) -> str:
    """
    Generate a complete HTML document for the given document type.

    Args:
        doc_type: One of the keys in DOCUMENT_TEMPLATES
        customer: Customer data dictionary
        extra_placeholders: Additional placeholder overrides

    Returns:
        Complete HTML string ready for PDF conversion
    """
    if doc_type not in DOCUMENT_TEMPLATES:
        raise ValueError(f"Unknown document type: {doc_type}. Available: {list(DOCUMENT_TEMPLATES.keys())}")

    template_name = DOCUMENT_TEMPLATES[doc_type]
    placeholders = get_default_placeholders(customer)

    if extra_placeholders:
        placeholders.update(extra_placeholders)

    return render_template(template_name, placeholders)


def generate_estate_plan_package(customer: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate all 6 documents in the estate plan package.

    Returns:
        Dict mapping document type keys to HTML strings
    """
    package = {}
    for doc_type in DOCUMENT_TEMPLATES:
        package[doc_type] = generate_document(doc_type, customer)
    return package


def get_available_documents() -> Dict[str, str]:
    """Return the list of available document types and their display names."""
    return dict(DOCUMENT_NAMES)
