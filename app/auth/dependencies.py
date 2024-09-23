from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request

from .jwt import AccessToken


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    def verify_jwt(token: str) -> bool:
        """
        Checks that token is valid and unexpired
        :param token: jwt token that will be checked
        :return: returns result of the check
        """
        is_token_valid: bool = True

        try:
            payload = AccessToken().decode_token(token)
        except Exception as e:
            is_token_valid = False

        return is_token_valid
