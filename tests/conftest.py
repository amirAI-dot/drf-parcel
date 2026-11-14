"""What every test may ask for: a client that speaks to the test project."""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client() -> APIClient:
    """A client that asks for JSON, as a frontend does."""
    return APIClient()
