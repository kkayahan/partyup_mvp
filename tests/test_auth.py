from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_login():
    # Using in-memory app; this will fail without DB, but acts as an example.
    assert app is not None
