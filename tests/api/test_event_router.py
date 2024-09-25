import json

import pytest

from httpx import AsyncClient
from starlette import status

from tests.conftest import USER_REQUEST_BODY


async def test_send_event_without_auth(client: AsyncClient, destinations) -> None:

    response = await client.post(
        url="api/v1/event/handle-event",
        data=USER_REQUEST_BODY
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_send_event(client: AsyncClient, destinations) -> None:
    awaited_result = {'destination1': True, 'destination2': False, 'destination3': True, 'destination43': False}

    response = await client.get(url="api/v1/auth/get-token")

    assert response.status_code == status.HTTP_200_OK
    access_token = response.json().get('access_token')

    client.headers.update({'Authorization': f'Bearer {access_token}'})

    response = await client.post(
        url="api/v1/event/handle-event",
        data=json.dumps(USER_REQUEST_BODY.copy())
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data
    assert response_data == awaited_result
