import os
import sys
from pathlib import Path
import pytest

# Ensure backend root is on sys.path so 'app' can be imported when running from repo root
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import create_app


@pytest.fixture()
def client():
    os.environ.setdefault("FLASK_ENV", "testing")
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    with app.test_client() as client:
        yield client
