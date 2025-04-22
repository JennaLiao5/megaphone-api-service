from fastapi import FastAPI
import logging
from app.db import init_db, SessionLocal
from app.apis.campaigns import router as campaign_router
from app.apis.remote import router as remote_router
from app.apis.sync import router as sync_router

from apscheduler.schedulers.background import BackgroundScheduler
from app.cruds.sync import sync_all_campaigns
from datetime import datetime
from app.logger import configure_logging

configure_logging()

app = FastAPI()
init_db()

# --- Add FastAPI router ---
app.include_router(campaign_router)
app.include_router(remote_router)
app.include_router(sync_router)

# --- Initialize APScheduler ---
scheduler = BackgroundScheduler()

def sync_job():
    try:
        with SessionLocal() as db:
            sync_all_campaigns(db)
        logging.info("Sync job completed.")
    except Exception as e:
        logging.exception("Scheduled sync failed")

scheduler.add_job(
    sync_job,
    'interval',
    minutes=30,
    next_run_time=datetime.utcnow()     # Execute immediately upon startup
)

# --- Automatically start scheduler ---
@app.on_event("startup")
def startup_event():
    if not scheduler.running:
        scheduler.start()
        logging.info("Scheduler started.")
