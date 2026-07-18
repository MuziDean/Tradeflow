"""
Settings validators.

Validates business preferences and configuration payloads.
"""


def validate_business_preferences(data: dict) -> list[str]:
    """Validate business preferences payload. Returns list of error messages."""
    errors = []
    if not data.get("default_currency_code"):
        errors.append("default_currency_code is required")
    if not data.get("timezone"):
        errors.append("timezone is required")
    if not data.get("locale"):
        errors.append("locale is required")
    return errors


def validate_fiscal_year(data: dict) -> list[str]:
    """Validate fiscal year payload. Returns list of error messages."""
    errors = []
    if not data.get("name"):
        errors.append("name is required")
    if not data.get("start_date"):
        errors.append("start_date is required")
    if not data.get("end_date"):
        errors.append("end_date is required")
    return errors


def validate_tax_configuration(data: dict) -> list[str]:
    """Validate tax configuration payload. Returns list of error messages."""
    errors = []
    if not data.get("name"):
        errors.append("name is required")
    if not data.get("rate"):
        errors.append("rate is required")
    return errors