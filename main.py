from fastapi import FastAPI
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()  # Also print to the console
    ]
)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to Megaphone API Service"}
