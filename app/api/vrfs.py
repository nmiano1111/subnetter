from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import VrfCreate, VrfUpdate, VrfOut, Page
from app.core.deps import get_db
from app.services import ipam as svc

router = APIRouter(prefix="/v1/vrfs", tags=["vrfs"])

@router.post("", response_model=VrfOut, status_code=201)
async def create_vrf(body: VrfCreate, db: AsyncSession = Depends(get_db)):
    return await svc.create_vrf(db, body)

@router.get("/{vrf_id}", response_model=VrfOut)
async def get_vrf(vrf_id: str, db: AsyncSession = Depends(get_db)):
    return await svc.get_vrf(db, vrf_id)

@router.get("", response_model=Page[VrfOut])
async def list_vrfs(tenant_id: str | None = None, q: str | None = None, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await svc.list_vrfs(db, tenant_id=tenant_id, q=q, limit=limit, offset=offset)

@router.patch("/{vrf_id}", response_model=VrfOut)
async def update_vrf(vrf_id: str, body: VrfUpdate, db: AsyncSession = Depends(get_db)):
    return await svc.update_vrf(db, vrf_id, body)

@router.delete("/{vrf_id}", status_code=204)
async def delete_vrf(vrf_id: str, db: AsyncSession = Depends(get_db)):
    await svc.delete_vrf(db, vrf_id)
