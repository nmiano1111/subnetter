# app/core/idempotency.py
from fastapi import Header
from typing import Annotated, Optional

IdemKey = Annotated[Optional[str], Header(alias="Idempotency-Key", description="Optional key to make POST idempotent")]
