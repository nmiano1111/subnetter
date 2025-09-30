# app/core/pagination.py
from fastapi import Query
from typing import Annotated

Limit = Annotated[int, Query(ge=1, le=200, description="items per page")]
Offset = Annotated[int, Query(ge=0, description="offset for pagination")]
