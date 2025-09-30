# models.py
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.orm import relationship as sa_relationship  # 👈 explicit SA relationship


class Tenant(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # one-to-many VRFs (explicit SA relationship target)
    vrfs: list["VRF"] = Relationship(
        back_populates="tenant",
        sa_relationship=sa_relationship("VRF", cascade="all, delete-orphan"),
    )


class VRF(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenant.id")
    name: str
    rd: Optional[str] = Field(default=None, index=True, max_length=128)  # <-- added
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # many-to-one Tenant
    tenant: Optional["Tenant"] = Relationship(
        back_populates="vrfs",
        sa_relationship=sa_relationship("Tenant"),
    )

    # one-to-many Prefix
    prefixes: list["Prefix"] = Relationship(
        back_populates="vrf",
        sa_relationship=sa_relationship("Prefix", cascade="all, delete-orphan"),
    )


class Prefix(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    vrf_id: UUID = Field(foreign_key="vrf.id")
    cidr: str
    status: str  # "container" | "active" | "reserved"
    description: str = ""
    parent_id: Optional[UUID] = Field(default=None, foreign_key="prefix.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # many-to-one VRF
    vrf: Optional["VRF"] = Relationship(
        back_populates="prefixes",
        sa_relationship=sa_relationship("VRF"),
    )

    # self-referential parent/children
    parent: Optional["Prefix"] = Relationship(
        back_populates="children",
        sa_relationship=sa_relationship("Prefix", remote_side="Prefix.id"),
    )
    children: list["Prefix"] = Relationship(
        back_populates="parent",
        sa_relationship=sa_relationship("Prefix"),
    )


class IPAddress(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    vrf_id: UUID = Field(foreign_key="vrf.id")
    prefix_id: UUID = Field(foreign_key="prefix.id")
    address: str
    status: str = "active"  # or "reserved"
    note: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
