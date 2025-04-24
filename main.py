from fastapi import FastAPI
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from app.db import init_db, SessionLocal
from app.apis.campaigns import router as campaign_router
from app.apis.remote import router as remote_router
from app.apis.sync import router as sync_router

from app.cruds.sync import sync_all_campaigns, sync_all_advertisers
from app.logger import configure_logging

configure_logging()

# --- Initialize APScheduler ---
scheduler = BackgroundScheduler()

def sync_job():
    try:
        with SessionLocal() as db:
            res = sync_all_advertisers(db)
            logging.info(
                f"Sync advertisers completed. "
                f"Successful (Add/Update): {res.get('upserted', 0)}, "
                f"Failed: {res.get('failed', 0)}, "
                f"Deleted: {res.get('deleted', 0)}."
            )
            res = sync_all_campaigns(db)
            logging.info(
                f"Sync campaigns completed. "
                f"Successful (Add/Update): {res.get('upserted', 0)}, "
                f"Failed: {res.get('failed', 0)}, "
                f"Deleted: {res.get('deleted', 0)}."

            )
        logging.info("Sync job completed.")
    except Exception:
        logging.exception("Scheduled sync failed")

scheduler.add_job(
    sync_job,
    'interval',
    minutes=30,
    next_run_time=datetime.utcnow()
)

# --- Automatically start scheduler ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if "pytest" not in sys.modules:
        scheduler.start()
        logging.info("Scheduler started.")
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logging.info("Scheduler shut down.")

# --- Create app with lifespan ---
app = FastAPI(lifespan=lifespan)

# --- Add FastAPI router ---
app.include_router(campaign_router)
app.include_router(remote_router)
app.include_router(sync_router)
