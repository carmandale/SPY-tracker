"""
Test configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)