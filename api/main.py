from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings
from loguru import logger
# from fastapi_utils.tasks import repeat_every
from contextlib import asynccontextmanager
import asyncio

from app.main import setup_bot

from db.admin import attach_admin_panel


class ProjectSettings(BaseSettings):
    LOCAL_MODE: bool = False


def register_exception(application):
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        # or logger.error(f'{exc}')
        logger.debug(f'{exc}')
        content = {'status_code': 422, 'message': exc_str, 'data': None}
        return JSONResponse(
            content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


def register_cors(application):
    application.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@asynccontextmanager
async def application_lifespan(app: FastAPI):
    bot_events = setup_bot(app)
    if bot_events is not None:
        on_startup, on_shutdown = bot_events
    else:
        yield
        return

    if asyncio.iscoroutinefunction(on_startup):
        await on_startup()
    else:
        on_startup()
    yield
    if asyncio.iscoroutinefunction(on_shutdown):
        await on_shutdown()
    else:
        on_shutdown()


def init_web_application():
    project_settings = ProjectSettings()
    application = FastAPI(
        openapi_url='/openapi.json',
        docs_url='/docs',
        redoc_url='/redoc',
        lifespan=application_lifespan
    )

    if project_settings.LOCAL_MODE:
        register_exception(application)
        register_cors(application)

    from api.routes.task import router as task_router

    application.include_router(task_router)

    attach_admin_panel(application)

    return application


def run() -> FastAPI:
    application = init_web_application()
    return application


fastapi_app = run()
