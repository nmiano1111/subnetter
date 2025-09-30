# app/api/schemas.py
from __future__ import annotations

import ipaddress
import uuid
from datetime import datetime
from enum import StrEnum
from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.generics import GenericModel


# =====================
# Shared base + enums
# =====================

class APIModel(BaseModel):
    """Base for request/response models (no ORM coupling)."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ORMModel(APIModel):
    """Base for models returned from ORM rows."""
    model_config = ConfigDict(from_attributes=True)


class PrefixStatus(StrEnum):
    container = "container"
    active = "active"
    reserved = "reserved"


class IPStatus(StrEnum):
    active = "active"
    reserved = "reserved"


# =====================
# Common wrappers
# =====================

T = TypeVar("T")

class Page(GenericModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class ErrorResponse(APIModel):
    error: Literal[
        "validation_error",
        "conflict",
        "not_found",
        "unauthorized",
        "forbidden",
        "rate_limited",
        "internal",
    ]
    message: str
    details: dict | None = None


# =====================
# Tenant
# =====================

class TenantCreate(APIModel):
    name: str = Field(min_length=1, max_length=128)


class TenantUpdate(APIModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)


class TenantOut(ORMModel):
    id: uuid.UUID
    name: str
    created_at: datetime


# =====================
# VRF
# =====================

class VrfCreate(APIModel):
    tenant_id: uuid.UUID
    name: str = Field(min_length=1, max_length=128)
    rd: Optional[str] = Field(
        default=None,
        max_length=128,
        description="Optional route distinguisher (free-form for prototype).",
    )


class VrfUpdate(APIModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    rd: Optional[str] = Field(default=None, max_length=128)


class VrfOut(ORMModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    rd: Optional[str] = None
    created_at: datetime


# =====================
# Prefix
# =====================

class PrefixBase(APIModel):
    vrf_id: uuid.UUID
    cidr: str = Field(description="Canonical CIDR, e.g. 10.0.0.0/16 or 2001:db8::/32")
    status: PrefixStatus
    description: Optional[str] = Field(default="", max_length=512)

    @field_validator("cidr")
    @classmethod
    def _canon_cidr(cls, v: str) -> str:
        try:
            net = ipaddress.ip_network(v, strict=True)
        except ValueError as e:
            raise ValueError(f"invalid CIDR: {e}") from e
        # Normalize to canonical string (compressed, no host bits)
        return str(net)


class PrefixCreate(PrefixBase):
    pass


class PrefixUpdate(APIModel):
    status: Optional[PrefixStatus] = None
    description: Optional[str] = Field(default=None, max_length=512)
    # Intentionally exclude cidr/vrf_id from PATCH for MVP. Use PUT/replace if you add that flow.


class PrefixOut(ORMModel):
    id: uuid.UUID
    vrf_id: uuid.UUID
    cidr: str
    status: PrefixStatus
    description: str
    parent_id: Optional[uuid.UUID] = None
    created_at: datetime


# =====================
# IP Address
# =====================

class IPCreate(APIModel):
    vrf_id: uuid.UUID
    prefix_id: uuid.UUID
    address: str = Field(description="Canonical IP address (IPv4 or IPv6)")
    status: IPStatus = IPStatus.active
    note: Optional[str] = Field(default="", max_length=512)

    @field_validator("address")
    @classmethod
    def _canon_ip(cls, v: str) -> str:
        try:
            ip = ipaddress.ip_address(v)
        except ValueError as e:
            raise ValueError(f"invalid IP address: {e}") from e
        return str(ip)


class IPUpdate(APIModel):
    status: Optional[IPStatus] = None
    note: Optional[str] = Field(default=None, max_length=512)


class IPOut(ORMModel):
    id: uuid.UUID
    vrf_id: uuid.UUID
    prefix_id: uuid.UUID
    address: str
    status: IPStatus
    note: str
    created_at: datetime


# =====================
# Actions / utilities
# =====================

class CarveChildrenIn(APIModel):
    mask: int = Field(ge=0, le=128)
    count: int = Field(default=1, ge=1, le=4096)
    strategy: Literal["first-fit", "dense"] = "first-fit"


class FreeSpaceOut(APIModel):
    cidr: str


class NextIPOut(APIModel):
    id: uuid.UUID
    address: str
