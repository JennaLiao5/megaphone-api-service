from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from app.db import init_db
from app.apis.campaigns import router as campaign_router
from app.apis.remote import router as remote_router
from app.apis.sync import router as sync_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()  # Also print to the console
    ]
)

app = FastAPI()
init_db()
app.include_router(campaign_router)
app.include_router(remote_router)
app.include_router(sync_router)
