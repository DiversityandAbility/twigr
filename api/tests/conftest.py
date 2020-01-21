import pytest
from starlette.testclient import TestClient

from app.main import app as app_


@pytest.fixture
def app():
    return app_


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client
