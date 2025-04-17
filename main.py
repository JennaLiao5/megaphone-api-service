from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from app import api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()  # Also print to the console
    ]
)

app = FastAPI()
app.include_router(api.router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Keep only the msg string for each error. 
    errors = [err["msg"] for err in exc.errors()]
    return JSONResponse(status_code=400, content={"errors": errors})
