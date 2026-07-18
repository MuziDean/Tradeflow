"""
Branch validators.

Validates branch creation and update payloads.
"""


def validate_branch_creation(data: dict) -> list[str]:
    """Validate branch creation payload. Returns list of error messages."""
    errors = []
    if not data.get("name"):
        errors.append("name is required")
    if not data.get("company_id"):
        errors.append("company_id is required")
    if not data.get("tenant_id"):
        errors.append("tenant_id is required")
    return errors


def validate_branch_update(data: dict) -> list[str]:
    """Validate branch update payload. Returns list of error messages."""
    errors = []
    if not data.get("id"):
        errors.append("id is required")
    return errors