from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import IPCreate, IPUpdate, IPOut, Page
from app.core.deps import get_db
from app.services import ipam as svc

router = APIRouter(prefix="/v1/ips", tags=["ips"])

@router.post("", response_model=IPOut, status_code=201)
async def create_ip(body: IPCreate, db: AsyncSession = Depends(get_db)):
    return await svc.create_ip(db, body)

@router.get("/{ip_id}", response_model=IPOut)
async def get_ip(ip_id: str, db: AsyncSession = Depends(get_db)):
    return await svc.get_ip(db, ip_id)

@router.get("", response_model=Page[IPOut])
async def list_ips(
    vrf_id: str | None = None,
    prefix_id: str | None = None,
    status: str | None = None,
    address: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    return await svc.list_ips(db, vrf_id=vrf_id, prefix_id=prefix_id, status=status, address=address, limit=limit, offset=offset)

@router.patch("/{ip_id}", response_model=IPOut)
async def update_ip(ip_id: str, body: IPUpdate, db: AsyncSession = Depends(get_db)):
    return await svc.update_ip(db, ip_id, body)

@router.delete("/{ip_id}", status_code=204)
async def delete_ip(ip_id: str, db: AsyncSession = Depends(get_db)):
    await svc.delete_ip(db, ip_id)
