from fastapi import FastAPI
from app.api import tenants, vrfs, prefixes, ips
from app.db.db import init_db

app = FastAPI(title="Subnetter API", version="1.0")

app.include_router(tenants.router)
app.include_router(vrfs.router)
app.include_router(prefixes.router)
app.include_router(ips.router)



@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/healthz")
async def healthz(): return {"ok": True}
