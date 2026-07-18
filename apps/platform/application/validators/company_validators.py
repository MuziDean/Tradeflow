"""
Company validators.

Validates company creation and update payloads.
"""


def validate_company_creation(data: dict) -> list[str]:
    """Validate company creation payload. Returns list of error messages."""
    errors = []
    if not data.get("legal_name"):
        errors.append("legal_name is required")
    if not data.get("tenant_id"):
        errors.append("tenant_id is required")
    return errors


def validate_company_update(data: dict) -> list[str]:
    """Validate company update payload. Returns list of error messages."""
    errors = []
    if not data.get("id"):
        errors.append("id is required")
    return errors