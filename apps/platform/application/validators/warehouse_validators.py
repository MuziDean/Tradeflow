"""
Warehouse validators.

Validates warehouse creation and update payloads.
"""


def validate_warehouse_creation(data: dict) -> list[str]:
    """Validate warehouse creation payload. Returns list of error messages."""
    errors = []
    if not data.get("name"):
        errors.append("name is required")
    if not data.get("branch_id"):
        errors.append("branch_id is required")
    if not data.get("warehouse_type"):
        errors.append("warehouse_type is required")
    return errors


def validate_warehouse_update(data: dict) -> list[str]:
    """Validate warehouse update payload. Returns list of error messages."""
    errors = []
    if not data.get("id"):
        errors.append("id is required")
    return errors