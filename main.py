from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .db import init_db
from .config import SCAN_INTERVAL_MINUTES
from .scanner import scan_once
from .repository import list_verified, register_device
from .models import DeviceRegistration
from .api_serialization import row_to_api

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler.add_job(scan_once, "interval", minutes=SCAN_INTERVAL_MINUTES, max_instances=1, coalesce=True)
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)

app = FastAPI(title="SweepHunter Pro", version="1.0.0", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"ok": True, "scanEveryMinutes": SCAN_INTERVAL_MINUTES}

@app.get("/v1/giveaways/verified")
async def verified():
    return {"results":[row_to_api(r) for r in list_verified()]}

@app.post("/v1/devices/register")
async def devices(reg: DeviceRegistration):
    register_device(reg.token, reg.platform)
    return {"ok": True}

@app.post("/v1/admin/scan")
async def run_scan():
    return await scan_once()
