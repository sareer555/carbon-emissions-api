import os

os.environ["DATABASE_URL"] = "sqlite:///./test_carbon_emissions.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import rate_limit
from app.auth import hash_key
from app.database import Base, get_db
from app.main import app
from app.models import ApiKey
from app.seed.factors_data import ALL_FACTORS
from app.models import EmissionFactor

TEST_DB_URL = "sqlite:///./test_carbon_emissions.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    for row in ALL_FACTORS:
        db.add(EmissionFactor(**row))
    db.commit()
    db.close()
    # Each test gets a fresh burst-rate-limit counter too, otherwise the
    # module-level in-memory limiter accumulates counts across tests that
    # reuse the same api_key id within the same 60-second window.
    rate_limit._limiter = rate_limit.InMemoryWindowLimiter(rate_limit.settings.burst_limit_per_minute)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def api_key():
    """Creates a free-plan API key directly in the test DB and returns the plaintext key."""
    db = TestingSessionLocal()
    plaintext = "cek_test_key_free"
    db.add(ApiKey(key_hash=hash_key(plaintext), plan="free", label="test"))
    db.commit()
    db.close()
    return plaintext


@pytest.fixture
def auth_headers(api_key):
    return {"Authorization": f"Bearer {api_key}"}
