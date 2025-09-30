from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette_exporter import PrometheusMiddleware, handle_metrics
from prometheus_client import Counter, Histogram

from app.api import tenants, vrfs, prefixes, ips
from app.db.db import init_db

app = FastAPI(
    title="Subnetter API",
    version="1.0",
    middleware=[Middleware(PrometheusMiddleware, group_paths=True)]
)

app.add_route("/metrics", handle_metrics)

subnet_calc_total = Counter("subnetter_calc_total", "Total subnet calculations", ["cidr"])
subnet_calc_errors = Counter("subnetter_calc_errors", "Subnet calc errors")
subnet_calc_seconds = Histogram("subnetter_calc_seconds", "Latency of subnet calc")


app.include_router(tenants.router)
app.include_router(vrfs.router)
app.include_router(prefixes.router)
app.include_router(ips.router)



@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/healthz")
async def healthz(): return {"ok": True}


@app.get("/subnet")
def subnet(cidr: str):
    with subnet_calc_seconds.time():
        try:
            # ... your calc ...
            subnet_calc_total.labels(cidr=cidr).inc()
            return {"ok": True}
        except Exception:
            subnet_calc_errors.inc()
            raise