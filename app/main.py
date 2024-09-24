
from fastapi import FastAPI

from .api import api_router
from .config import get_settings
from .middleware import RequestLoggingMiddleware


def get_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI()

    application.include_router(api_router, prefix='/api/v1')

    application.add_middleware(RequestLoggingMiddleware)

    return application


app = get_application()
