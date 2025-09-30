# app/services/ipam.py
from __future__ import annotations

import ipaddress
import uuid
from typing import Optional

from sqlmodel import select  # ✅ use sqlmodel.select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    TenantCreate, TenantUpdate, TenantOut,
    VrfCreate, VrfUpdate, VrfOut,
    PrefixCreate, PrefixUpdate, PrefixOut,
    CarveChildrenIn, FreeSpaceOut, NextIPOut,
    IPCreate, IPUpdate, IPOut, Page,
    PrefixStatus, IPStatus,
)
from app.core.errors import NotFound, Conflict, ValidationErr
from app.db import models as m


# -----------------
# helpers
# -----------------

def _parse_net(cidr: str) -> ipaddress._BaseNetwork:  # type: ignore[name-defined]
    try:
        return ipaddress.ip_network(cidr, strict=True)
    except ValueError as e:
        raise ValidationErr(f"invalid CIDR: {e}")

def _canon_ip(v: str) -> str:
    try:
        return str(ipaddress.ip_address(v))
    except ValueError as e:
        raise ValidationErr(f"invalid IP address: {e}")

def _status_val(s: PrefixStatus | IPStatus | str | None) -> Optional[str]:
    if s is None:
        return None
    return s.value if hasattr(s, "value") else str(s)


# -----------------
# Tenants
# -----------------

async def create_tenant(db: AsyncSession, body: TenantCreate) -> TenantOut:
    t = m.Tenant(name=body.name)
    db.add(t)
    await db.flush()
    await db.refresh(t)
    await db.commit()  # ✅ commit
    return TenantOut.model_validate(t)

async def get_tenant(db: AsyncSession, tenant_id: str) -> TenantOut:
    t = await db.get(m.Tenant, uuid.UUID(tenant_id))
    if not t:
        raise NotFound("tenant not found")
    return TenantOut.model_validate(t)

async def list_tenants(db: AsyncSession, q: str | None, limit: int, offset: int) -> Page[TenantOut]:
    stmt = select(m.Tenant)
    if q:
        stmt = stmt.where(m.Tenant.name.ilike(f"%{q}%"))
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    rows = (await db.execute(stmt.order_by(m.Tenant.created_at.desc()).limit(limit).offset(offset))).scalars().all()
    return Page[TenantOut](items=[TenantOut.model_validate(r) for r in rows], total=total, limit=limit, offset=offset)

async def update_tenant(db: AsyncSession, tenant_id: str, body: TenantUpdate) -> TenantOut:
    t = await db.get(m.Tenant, uuid.UUID(tenant_id))
    if not t:
        raise NotFound("tenant not found")
    if body.name is not None:
        t.name = body.name
    await db.flush()
    await db.refresh(t)
    await db.commit()  # ✅
    return TenantOut.model_validate(t)

async def delete_tenant(db: AsyncSession, tenant_id: str) -> None:
    t = await db.get(m.Tenant, uuid.UUID(tenant_id))
    if not t:
        return
    await db.delete(t)
    await db.commit()  # ✅


# -----------------
# VRFs
# -----------------

async def create_vrf(db: AsyncSession, body: VrfCreate) -> VrfOut:
    if not await db.get(m.Tenant, body.tenant_id):
        raise ValidationErr("tenant_id does not exist")
    row = m.VRF(tenant_id=body.tenant_id, name=body.name, rd=body.rd)
    db.add(row)
    await db.flush()
    await db.refresh(row)
    await db.commit()  # ✅
    return VrfOut.model_validate(row)

async def get_vrf(db: AsyncSession, vrf_id: str) -> VrfOut:
    row = await db.get(m.VRF, uuid.UUID(vrf_id))
    if not row:
        raise NotFound("vrf not found")
    return VrfOut.model_validate(row)

async def list_vrfs(db: AsyncSession, tenant_id: str | None, q: str | None, limit: int, offset: int) -> Page[VrfOut]:
    stmt = select(m.VRF)
    if tenant_id:
        stmt = stmt.where(m.VRF.tenant_id == uuid.UUID(tenant_id))
    if q:
        stmt = stmt.where(m.VRF.name.ilike(f"%{q}%"))
    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    rows = (await db.execute(stmt.order_by(m.VRF.created_at.desc()).limit(limit).offset(offset))).scalars().all()
    return Page[VrfOut](items=[VrfOut.model_validate(r) for r in rows], total=total, limit=limit, offset=offset)

async def update_vrf(db: AsyncSession, vrf_id: str, body: VrfUpdate) -> VrfOut:
    row = await db.get(m.VRF, uuid.UUID(vrf_id))
    if not row:
        raise NotFound("vrf not found")
    if body.name is not None:
        row.name = body.name
    if body.rd is not None:
        row.rd = body.rd
    await db.flush()
    await db.refresh(row)
    await db.commit()  # ✅
    return VrfOut.model_validate(row)

async def delete_vrf(db: AsyncSession, vrf_id: str) -> None:
    row = await db.get(m.VRF, uuid.UUID(vrf_id))
    if not row:
        return
    await db.delete(row)
    await db.commit()  # ✅


# -----------------
# Prefixes
# -----------------

async def create_prefix(db: AsyncSession, body: PrefixCreate, idem: str | None) -> PrefixOut:
    new_net = _parse_net(body.cidr)
    new_status = _status_val(body.status)

    # naive overlap check inside VRF (prototype)
    existing = (await db.execute(select(m.Prefix).where(m.Prefix.vrf_id == body.vrf_id))).scalars().all()
    for e in existing:
        e_net = _parse_net(e.cidr)
        if new_status in {"active", "reserved"} and e.status in {"active", "reserved"} and new_net.overlaps(e_net):
            raise Conflict(f"prefix {body.cidr} overlaps existing {e.cidr}")

    row = m.Prefix(
        vrf_id=body.vrf_id,
        cidr=str(new_net),
        status=new_status or "active",
        description=body.description or "",
    )
    db.add(row)
    await db.flush()
    await db.refresh(row)
    await db.commit()  # ✅
    return PrefixOut.model_validate(row)

async def get_prefix(db: AsyncSession, prefix_id: str) -> PrefixOut:
    row = await db.get(m.Prefix, uuid.UUID(prefix_id))
    if not row:
        raise NotFound("prefix not found")
    return PrefixOut.model_validate(row)

async def update_prefix(db: AsyncSession, prefix_id: str, body: PrefixUpdate) -> PrefixOut:
    row = await db.get(m.Prefix, uuid.UUID(prefix_id))
    if not row:
        raise NotFound("prefix not found")
    if body.status is not None:
        row.status = _status_val(body.status) or row.status
    if body.description is not None:
        row.description = body.description
    await db.flush()
    await db.refresh(row)
    await db.commit()  # ✅
    return PrefixOut.model_validate(row)

async def delete_prefix(db: AsyncSession, prefix_id: str) -> None:
    row = await db.get(m.Prefix, uuid.UUID(prefix_id))
    if not row:
        return
    await db.delete(row)
    await db.commit()  # ✅

async def list_prefixes(
    db: AsyncSession,
    vrf_id: str | None,
    status: str | None,
    cidr_contains: str | None,
    limit: int,
    offset: int,
) -> Page[PrefixOut]:
    stmt = select(m.Prefix)
    if vrf_id:
        stmt = stmt.where(m.Prefix.vrf_id == uuid.UUID(vrf_id))
    if status:
        stmt = stmt.where(m.Prefix.status == _status_val(status))
    raw_total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    rows = (await db.execute(stmt.order_by(m.Prefix.created_at.desc()).limit(limit).offset(offset))).scalars().all()

    # Optional Python-side containment filter (prototype)
    if cidr_contains:
        block = _parse_net(cidr_contains)
        rows = [r for r in rows if _parse_net(r.cidr).subnet_of(block) or block.supernet_of(_parse_net(r.cidr))]
        total = len(rows)  # make total reflect filter
    else:
        total = raw_total

    return Page[PrefixOut](items=[PrefixOut.model_validate(r) for r in rows], total=total, limit=limit, offset=offset)

async def free_space(db: AsyncSession, prefix_id: str, mask: int) -> list[FreeSpaceOut]:
    parent = await db.get(m.Prefix, uuid.UUID(prefix_id))
    if not parent:
        raise NotFound("parent prefix not found")
    parent_net = _parse_net(parent.cidr)
    if mask < parent_net.prefixlen:
        raise ValidationErr("mask must be >= parent mask")

    # collect used child blocks at that mask
    kids = (await db.execute(select(m.Prefix).where(m.Prefix.parent_id == parent.id))).scalars().all()
    used = [_parse_net(k.cidr) for k in kids if _parse_net(k.cidr).prefixlen == mask]

    out: list[FreeSpaceOut] = []
    for cand in parent_net.subnets(new_prefix=mask):
        if any(cand.overlaps(u) for u in used):
            continue
        out.append(FreeSpaceOut(cidr=str(cand)))
    return out

async def carve_children(db: AsyncSession, prefix_id: str, body: CarveChildrenIn, idem: str | None) -> list[PrefixOut]:
    parent = await db.get(m.Prefix, uuid.UUID(prefix_id))
    if not parent:
        raise NotFound("parent prefix not found")
    parent_net = _parse_net(parent.cidr)
    if body.mask < parent_net.prefixlen:
        raise ValidationErr("mask must be >= parent mask")

    kids = (await db.execute(select(m.Prefix).where(m.Prefix.parent_id == parent.id))).scalars().all()
    existing = [_parse_net(k.cidr) for k in kids]

    allocated: list[PrefixOut] = []
    for cand in parent_net.subnets(new_prefix=body.mask):
        if any(cand.overlaps(e) for e in existing):
            continue
        row = m.Prefix(vrf_id=parent.vrf_id, cidr=str(cand), status="active", parent_id=parent.id)
        db.add(row)
        await db.flush()
        await db.refresh(row)
        allocated.append(PrefixOut.model_validate(row))
        if len(allocated) >= body.count:
            break

    if not allocated:
        raise Conflict("no free sub-prefixes")

    await db.commit()  # ✅ commit once after allocations
    return allocated


# -----------------
# IPs
# -----------------

async def create_ip(db: AsyncSession, body: IPCreate) -> IPOut:
    pfx = await db.get(m.Prefix, body.prefix_id)
    if not pfx:
        raise ValidationErr("prefix_id does not exist")
    net = _parse_net(pfx.cidr)
    ip = _canon_ip(body.address)
    if ipaddress.ip_address(ip) not in net:
        raise ValidationErr(f"{ip} not in {pfx.cidr}")

    dup = (await db.execute(
        select(m.IPAddress).where(m.IPAddress.vrf_id == body.vrf_id, m.IPAddress.address == ip)
    )).scalar_one_or_none()
    if dup:
        raise Conflict(f"IP {ip} already exists in VRF")

    row = m.IPAddress(
        vrf_id=body.vrf_id,
        prefix_id=body.prefix_id,
        address=ip,
        status=_status_val(body.status) or "active",
        note=body.note or "",
    )
    db.add(row)
    await db.flush()
    await db.refresh(row)
    await db.commit()  # ✅
    return IPOut.model_validate(row)

async def allocate_next_ip(db: AsyncSession, prefix_id: str, idem: str | None) -> NextIPOut:
    pfx = await db.get(m.Prefix, uuid.UUID(prefix_id))
    if not pfx:
        raise NotFound("prefix not found")
    net = _parse_net(pfx.cidr)

    taken = (await db.execute(select(m.IPAddress.address).where(m.IPAddress.prefix_id == pfx.id))).scalars().all()
    taken_set = {ipaddress.ip_address(a) for a in taken}

    for host in net.hosts():  # skips network/broadcast for IPv4
        if host not in taken_set:
            row = m.IPAddress(vrf_id=pfx.vrf_id, prefix_id=pfx.id, address=str(host), status="active")
            db.add(row)
            await db.flush()
            await db.refresh(row)
            await db.commit()  # ✅
            return NextIPOut(id=row.id, address=row.address)

    raise Conflict("no free IPs")

async def get_ip(db: AsyncSession, ip_id: str) -> IPOut:
    row = await db.get(m.IPAddress, uuid.UUID(ip_id))
    if not row:
        raise NotFound("ip not found")
    return IPOut.model_validate(row)

async def list_ips(
    db: AsyncSession,
    vrf_id: str | None,
    prefix_id: str | None,
    status: str | None,
    address: str | None,
    limit: int,
    offset: int,
) -> Page[IPOut]:
    stmt = select(m.IPAddress)
    if vrf_id:
        stmt = stmt.where(m.IPAddress.vrf_id == uuid.UUID(vrf_id))
    if prefix_id:
        stmt = stmt.where(m.IPAddress.prefix_id == uuid.UUID(prefix_id))
    if status:
        stmt = stmt.where(m.IPAddress.status == _status_val(status))
    if address:
        stmt = stmt.where(m.IPAddress.address == _canon_ip(address))

    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    rows = (await db.execute(stmt.order_by(m.IPAddress.created_at.desc()).limit(limit).offset(offset))).scalars().all()
    return Page[IPOut](items=[IPOut.model_validate(r) for r in rows], total=total, limit=limit, offset=offset)

async def update_ip(db: AsyncSession, ip_id: str, body: IPUpdate) -> IPOut:
    row = await db.get(m.IPAddress, uuid.UUID(ip_id))
    if not row:
        raise NotFound("ip not found")
    if body.status is not None:
        row.status = _status_val(body.status) or row.status
    if body.note is not None:
        row.note = body.note
    await db.flush()
    await db.refresh(row)
    await db.commit()  # ✅
    return IPOut.model_validate(row)

async def delete_ip(db: AsyncSession, ip_id: str) -> None:
    row = await db.get(m.IPAddress, uuid.UUID(ip_id))
    if not row:
        return
    await db.delete(row)
    await db.commit()  # ✅
