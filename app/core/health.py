from fastapi import APIRouter
health_router = APIRouter()
@health_router.get("/healthz")
async def healthz(): return {"status": "ok"}
@health_router.get("/readyz")
async def readyz(): return {"status": "ready"}
