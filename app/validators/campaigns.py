import re
from fastapi import HTTPException


def validate_budget_cents(v, field_name="This field"):
    if v is None:
        return v
    if isinstance(v, str):
        if not v.strip().isdigit():
            raise HTTPException(status_code=400, detail=f"{field_name} must be a valid integer")
        return int(v.strip())
    if not isinstance(v, int):
        raise HTTPException(status_code=400, detail=f"{field_name} must be a valid integer")
    if v < 0:
        raise HTTPException(status_code=400, detail=f"{field_name} must be a positive integer")
    return v


def validate_currency_code(v, field_name="This field"):
    if v is None:
        return v
    if isinstance(v, str) and not v.strip():
        raise HTTPException(status_code=400, detail=f"{field_name} must not be empty")
    if not re.fullmatch(r"^[A-Z]{3}$", v.strip()):
        raise HTTPException(status_code=400, detail=f"{field_name} must be a valid 3-letter uppercase code (e.g. USD)")
    return v.strip()