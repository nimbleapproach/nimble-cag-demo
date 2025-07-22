import os
import pytest
from fastapi.testclient import TestClient
from main import app

# Test configuration
API_URL = os.getenv("TEST_API_URL", "http://localhost:8000")
TIMEOUT = int(os.getenv("TEST_TIMEOUT", "300"))  # 5 minutes default

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
def api_url():
    """Get the API URL for testing"""
    return API_URL

@pytest.fixture
def timeout():
    """Get the timeout for tests"""
    return TIMEOUT 