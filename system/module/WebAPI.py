import asyncio
import uvicorn
from fastapi import FastAPI
# from fastapi.logger import logger
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from starlette.middleware.cors import CORSMiddleware

from system.module.logger import getlogger
from system.module.ymlconfig import YmlConfig, get_arguments
from system.connection.BaseConnection import init_connection
from system.module.Validator import Validator


class WebAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('cors'):
            self.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                                    allow_methods=["*"], allow_headers=["*"])
        self.config = YmlConfig(*get_arguments())
        self.logger = getlogger(self.config.app_name, self.config.logger)
        self.logger.handlers = self.logger.handlers[:1]
        self.connection = None
        self.add_exception_handler(RequestValidationError, self.my_exception_handler)
        # health_checker
        if health_checker := self.config.web_server.get('health_checker'):  # Работоспособность
            if health_checker.get('url_health') and health_checker.get('url_live'):
                self.logger.debug(f"Initialization of check working (url_health="
                                  f"{health_checker['url_health']} url_live={health_checker['url_live']})")

                @self.get(health_checker['url_live'])
                @self.get(health_checker['url_health'])
                async def url_health():
                    return {'ping': 'OK!'}

    async def init_connection(self):
        params = {'config': self.config, 'loop': asyncio.get_running_loop()}
        if await init_connection(
                self.config.connection, params, self.logger, None, self.config.web_server.get('connection')):
            del params['config']
            self.connection = params

    @staticmethod
    async def my_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({
                'status': {
                    'success': False,
                    'errors': Validator.error_pydantic_convert(exc.errors()),
                }
            })
        )

    @staticmethod
    def json_response(status_code, request):
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(request)
        )

    @staticmethod
    def run(app_name, **kwargs):
        uvicorn.run(app_name, **kwargs)
