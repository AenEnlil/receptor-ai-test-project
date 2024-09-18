from httpx import AsyncClient
from starlette import status


async def test_get_access_token(client: AsyncClient) -> None:
    response = await client.get(
        url="api/v1/auth/get-token"
    )

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data
    assert 'access_token' in response_data
