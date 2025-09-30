# app/api/routers/prefixes.py
from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    PrefixCreate, PrefixUpdate, PrefixOut, CarveChildrenIn, FreeSpaceOut, NextIPOut, Page,
)
from app.core.deps import get_db
from app.core.idempotency import IdemKey
from app.services import ipam as svc

router = APIRouter(prefix="/v1/prefixes", tags=["prefixes"])

@router.post("", response_model=PrefixOut, status_code=201)
async def create_prefix(body: PrefixCreate, db: AsyncSession = Depends(get_db), idem: IdemKey = None):
    return await svc.create_prefix(db, body, idem=idem)

@router.get("/{prefix_id}", response_model=PrefixOut)
async def get_prefix(prefix_id: str, db: AsyncSession = Depends(get_db)):
    return await svc.get_prefix(db, prefix_id)

@router.patch("/{prefix_id}", response_model=PrefixOut)
async def update_prefix(prefix_id: str, body: PrefixUpdate, db: AsyncSession = Depends(get_db)):
    return await svc.update_prefix(db, prefix_id, body)

@router.delete("/{prefix_id}", status_code=204)
async def delete_prefix(prefix_id: str, db: AsyncSession = Depends(get_db)):
    await svc.delete_prefix(db, prefix_id)

@router.get("", response_model=Page[PrefixOut])
async def list_prefixes(
    vrf_id: str | None = None,
    status: str | None = None,
    cidr_contains: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await svc.list_prefixes(db, vrf_id=vrf_id, status=status, cidr_contains=cidr_contains, limit=limit, offset=offset)

@router.post("/{prefix_id}/children", response_model=list[PrefixOut], status_code=201)
async def carve_children(prefix_id: str, body: CarveChildrenIn, db: AsyncSession = Depends(get_db), idem: IdemKey = None):
    return await svc.carve_children(db, prefix_id, body, idem=idem)

@router.get("/{prefix_id}/free-space", response_model=list[FreeSpaceOut])
async def free_space(prefix_id: str, mask: int, db: AsyncSession = Depends(get_db)):
    return await svc.free_space(db, prefix_id, mask)

@router.post("/{prefix_id}/ips/next", response_model=NextIPOut, status_code=201)
async def next_ip(prefix_id: str, db: AsyncSession = Depends(get_db), idem: IdemKey = None):
    return await svc.allocate_next_ip(db, prefix_id, idem=idem)
