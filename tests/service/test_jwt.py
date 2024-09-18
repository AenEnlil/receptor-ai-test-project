import jwt
import pytest

from datetime import datetime

from app.auth.exceptions import TokenError
from app.auth.jwt import AccessToken
from app.config import get_settings

SECRET_KEY = get_settings().SECRET_KEY
ALGORITHM = get_settings().ALGORITHM
TOKEN_LIFETIME = get_settings().ACCESS_TOKEN_LIFETIME_MINUTES


async def test_creating_jwt_token() -> None:
    token = AccessToken().create_access_token()

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload
    assert 'exp' in payload


async def test_decoding_jwt_token() -> None:
    token = AccessToken().create_access_token()

    payload = AccessToken().decode_token(token)

    assert payload
    assert 'exp' in payload


async def test_error_when_token_invalid() -> None:
    with pytest.raises(TokenError) as e:
        AccessToken().decode_token("dfgd")
    assert e.value.args[0] == 'token is incorrect'


async def test_error_when_token_expired() -> None:
    date = datetime(year=2020, month=1, day=12)
    token = AccessToken(date).create_access_token()

    with pytest.raises(TokenError) as e:
        AccessToken().decode_token(token)
    assert e.value.args[0] == 'token expired'
