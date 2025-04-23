import pytest
from fastapi.testclient import TestClient
from main import app as fastapi_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import app.db
import os

# Use a test database
TEST_DB_URL = "sqlite:///./test_campaign.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    app.db.SessionLocal = TestingSessionLocal
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_campaign.db"):
        try:
            os.remove("./test_campaign.db")
        except PermissionError:
            pass

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client():
    with TestClient(fastapi_app) as c:
        yield c
