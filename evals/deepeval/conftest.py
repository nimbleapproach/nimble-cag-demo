"""Pytest configuration for DeepEval tests."""
import pytest
import os


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Get the API base URL from environment or use default."""
    return os.getenv("CAG_API_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def openai_api_key() -> str:
    """Get OpenAI API key from environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not set")
    return key