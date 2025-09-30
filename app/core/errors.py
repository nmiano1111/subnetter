# app/core/errors.py
from fastapi import HTTPException, status
from typing import Any


class Conflict(HTTPException):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail={"error":"conflict","message":message,"details":details})


class NotFound(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail={"error":"not_found","message":message})


class ValidationErr(HTTPException):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"error":"validation_error","message":message,"details":details})
