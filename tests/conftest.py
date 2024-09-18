import pytest

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from typing import Generator, Any

from app.main import get_application


@pytest.fixture()
async def app() -> Generator[FastAPI, Any, None]:
    _app = get_application()
    yield _app


@pytest.fixture(scope="function")
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://') as test_client:
        yield test_client

