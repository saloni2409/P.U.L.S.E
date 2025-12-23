import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure the backend package root is on sys.path so `import app` works when pytest
# is invoked from different working directories.
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.core.database import Base, get_db
from main import app

# Use a temporary file-based SQLite DB for tests so multiple connections
# and sessions share the same schema and data.
TEST_DATABASE_PATH = os.path.join(ROOT, "test_sqlite_backend.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Prevent tests from making real LLM network calls by stubbing the provider
try:
    from app.core import llm_service

    class _DummyProvider:
        async def generate(self, prompt: str, max_tokens: int = 1000) -> str:
            # Return empty list JSON so parsing returns no items
            return "[]"

    llm_service.LLMService._provider = _DummyProvider()
except Exception:
    # If LLMService isn't available for any reason, continue without stubbing
    pass


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    # Create all tables once per test session
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """Provide a TestClient that uses the in-memory DB session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)
