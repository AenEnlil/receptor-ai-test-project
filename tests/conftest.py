import pytest

from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from typing import Generator, Any

from app.main import get_application
from app.config import get_settings
from app.database import mongo_client, DESTINATIONS_DOC, DEFAULT_STRATEGY_DOC

DESTINATIONS = {
    'destinations': [
        {
            'destinationName': 'destination1',
            'transport': 'http.get',
            'url': 'http://example.com'
         },
        {
            'destinationName': 'destination2',
            'transport': 'http.post',
            'url': 'http://example.com'
        },
        {
            'destinationName': 'destination3',
            'transport': 'log.info',
        },
        {
            'destinationName': 'destination4',
            'transport': 'log.warn',
        }
    ],
}
DEFAULT_STRATEGY = {'strategy': 'all'}

USER_REQUEST_BODY = {
    "payload": {"a": "1"},
    "routingIntents": [
        {
            "destinationName": "destination1",
            "important": True,
            "bytes": 15,
            "score": 0
        },
        {
            "destinationName": "destination2",
            "important": False
        },
        {
            "destinationName": "destination3",
            "bytes": 15,
            "score": 1
        },
        {
            "destinationName": "destination43",
            "bytes": 15,
            "score": 0
        }
    ],
    "strategy": "small"
}

settings = get_settings()

DATABASE_NAME = 'test_database'


@pytest.fixture()
async def app() -> Generator[FastAPI, Any, None]:
    _app = get_application()
    yield _app
    mongo_client.drop_database(settings.DATABASE_NAME)


@pytest.fixture(scope="function")
async def client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://') as test_client:
        yield test_client


@pytest.fixture
async def destinations():
    destinations = DESTINATIONS.get('destinations')
    mongo_client[settings.DATABASE_NAME].get_collection(DESTINATIONS_DOC).insert_many(destinations)
    return destinations


@pytest.fixture
async def default_strategy():
    strategy = DEFAULT_STRATEGY
    mongo_client[settings.DATABASE_NAME].get_collection(DEFAULT_STRATEGY_DOC).insert_one(strategy)
    return strategy
