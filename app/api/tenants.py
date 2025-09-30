from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import TenantCreate, TenantUpdate, TenantOut, Page
from app.core.deps import get_db
from app.services import ipam as svc

router = APIRouter(prefix="/v1/tenants", tags=["tenants"])


@router.post("", response_model=TenantOut, status_code=201)
async def create_tenant(body: TenantCreate, db: AsyncSession = Depends(get_db)):
    return await svc.create_tenant(db, body)


@router.get("/{tenant_id}", response_model=TenantOut)
async def get_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)):
    return await svc.get_tenant(db, tenant_id)


@router.get("", response_model=Page[TenantOut])
async def list_tenants(q: str | None = None, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await svc.list_tenants(db, q=q, limit=limit, offset=offset)


@router.patch("/{tenant_id}", response_model=TenantOut)
async def update_tenant(tenant_id: str, body: TenantUpdate, db: AsyncSession = Depends(get_db)):
    return await svc.update_tenant(db, tenant_id, body)


@router.delete("/{tenant_id}", status_code=204)
async def delete_tenant(tenant_id: str, db: AsyncSession = Depends(get_db)):
    await svc.delete_tenant(db, tenant_id)
