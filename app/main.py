import asyncio
import secrets
from os import getenv

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType
from aiogram.types import InputFile
from aiogram3_di import setup_di
from aiohttp import MultipartWriter
from loguru import logger

import app
from app import handlers


class MockClass:
    def __init__(self, *args, **kwargs):
        pass

    def __getattribute__(self, name):
        raise NotImplementedError("Mock class hasn't attributes")

try:
    from fastapi import FastAPI, HTTPException, Request, Response
except ImportError:
    FastAPI, HTTPException, Request, Response = MockClass, MockClass, MockClass, MockClass


BOT_ID = 'mailing_bot'
BOT_WEBHOOK_PATH = getenv('BOT_WEBHOOK_PATH', '/api/bot')
BOT_WEBHOOK_URL = getenv('BOT_WEBHOOK_URL')
BOT_TOKEN = getenv('BOT_TOKEN')


def _build_response_writer(
        result: TelegramMethod[TelegramType] | None
) -> MultipartWriter:
    writer = MultipartWriter(
        "form-data",
        boundary=f"webhookBoundary{secrets.token_urlsafe(16)}",
    )
    if not result:
        return writer

    payload = writer.append(result.__api_method__)
    payload.set_content_disposition("form-data", name="method")

    files: dict[str, InputFile] = {}
    for key, value in result.model_dump(warnings=False).items():
        value = bot.session.prepare_value(value, bot=bot, files=files)
        if not value:
            continue
        payload = writer.append(value)
        payload.set_content_disposition("form-data", name=key)

    for key, value in files.items():
        payload = writer.append(value.read(bot))
        payload.set_content_disposition(
            "form-data",
            name=key,
            filename=value.filename or key,
        )
    return writer


async def handle_webhook(request: Request) -> Response:
    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != BOT_ID:
        raise HTTPException(401)
    result = await app.dispatcher_instance.feed_webhook_update(
        app.bot_instance,
        app.bot_instance.session.json_loads(await request.body())
    )
    writer = _build_response_writer(result)
    response = Response(
        content=writer._value,
        headers=writer.headers,
        media_type=writer.content_type
    )
    return response


async def dispatcher_startup():
    try:
        await app.bot_instance.set_webhook(
            url=BOT_WEBHOOK_URL.rstrip('/') + BOT_WEBHOOK_PATH,
            secret_token=BOT_ID
        )
    except Exception as e:
        logger.error(e)
    else:
        logger.info("Bot started")


def _setup_dispatcher(dispatcher: Dispatcher):
    dispatcher.include_routers(handlers.task.router)
    setup_di(dispatcher)


def setup_bot(application: FastAPI):
    if not BOT_TOKEN:
        return
    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()
    _setup_dispatcher(dispatcher)

    app.bot_instance = bot
    app.dispatcher_instance = dispatcher

    if BOT_WEBHOOK_URL:
        dispatcher.startup.register(dispatcher_startup)

        async def on_startup() -> None:
            await dispatcher.emit_startup(
                application=application, dispatcher=dispatcher, **dispatcher.workflow_data
            )

        async def on_shutdown() -> None:
            await bot.session.close()
            await dispatcher.emit_startup(
                application=application, dispatcher=dispatcher, **dispatcher.workflow_data
            )

        application.add_route(
            path=BOT_WEBHOOK_PATH, route=handle_webhook, methods=["POST"]
        )
    else:
        def on_startup():
            asyncio.create_task(bot.delete_webhook())
            asyncio.create_task(dispatcher.start_polling(bot))

        def on_shutdown():
            asyncio.create_task(dispatcher.stop_polling())

    logger.info("Bot setup finished")
    return on_startup, on_shutdown


async def run_polling():
    global bot, dispatcher
    bot = Bot(token=BOT_TOKEN)
    dispatcher = Dispatcher()
    app.bot_instance = bot
    app.dispatcher_instance = dispatcher
    _setup_dispatcher(dispatcher)

    await bot.delete_webhook()
    logger.info("Bot started")
    await dispatcher.start_infinity_polling(bot)


if __name__ == '__main__':
    asyncio.run(run_polling())
