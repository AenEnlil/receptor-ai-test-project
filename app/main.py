
from fastapi import FastAPI, Depends

from .api import api_router
from .auth.dependencies import JWTBearer
from .config import get_settings
from .middleware import RequestLoggingMiddleware


def get_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI()

    application.include_router(api_router, prefix='/api/v1')

    application.add_middleware(RequestLoggingMiddleware)

    return application


app = get_application()


@app.get('/', dependencies=[Depends(JWTBearer())])
def read_root():
    return {'result': 'Hello World'}

