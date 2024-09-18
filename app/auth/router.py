from fastapi import APIRouter

from .jwt import AccessToken

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.get('/get-token')
async def get_access_token():
    return {"access_token": AccessToken().create_access_token()}
