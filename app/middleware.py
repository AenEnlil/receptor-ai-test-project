import json

from fastapi import Request
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse

from .database import get_logs_collection
from .logging_schemas import RequestLoggingSchema, ResponseLoggingSchema
from .utils import AsyncIteratorWrapper


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        prepared_request_data = await self.prepare_request_for_logging(request)

        try:
            response = await call_next(request)

            prepared_response_data = await self.prepare_response_for_logging(response)

            self.__log_to_db(prepared_request_data, prepared_response_data)

            return response
        except Exception as e:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            error_details = {'error': e.args[0]}
            response_error_data = ResponseLoggingSchema(status_code=status_code, body=error_details).model_dump()

            self.__log_to_db(prepared_request_data, response_error_data)

            return JSONResponse(status_code=status_code, content=error_details)

    async def set_body(self, request: Request):
        try:
            body = await request.json()
        except Exception:
            body = None
        return body

    async def prepare_request_for_logging(self, request: Request):

        request_data = dict(request.items())
        binary_headers = request_data.pop('headers')
        request_data.update({'headers': self.convert_binary_headers(binary_headers)})

        request_body = await self.set_body(request)
        request_data.update({'body': request_body})

        return RequestLoggingSchema(**request_data).model_dump()

    async def prepare_response_for_logging(self, response: Response):
        headers = self.convert_binary_headers(response.raw_headers)

        body_iterator = response.__dict__['body_iterator']
        binary_response_body = [section async for section in body_iterator]
        response.__setattr__("body_iterator", AsyncIteratorWrapper(binary_response_body))
        response_body = json.loads(binary_response_body[0].decode())
        return ResponseLoggingSchema(status_code=response.status_code, headers=headers, body=response_body).model_dump()

    @staticmethod
    def convert_binary_headers(binary_headers):
        return [{raw_header[0].decode(): raw_header[1].decode()} for raw_header in binary_headers]

    def __log_to_db(self, request_data: dict, response_data: dict):
        data = {'request': request_data, 'response': response_data}
        get_logs_collection().insert_one(data)
