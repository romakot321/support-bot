from typing import Annotated

from aiogram import F
from aiogram import Router
from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import PhotoSize
from aiogram.fsm.state import State
from aiogram3_di import Depends

from app.schemas.action_callback import Action, SupportActionCallback
from app.schemas.action_callback import ActionCallback
from app.services.support import SupportService

router = Router(name=__name__)


@router.message(CommandStart())
async def start_command(
    message: Message,
    bot: Bot,
    support_service: Annotated[SupportService, Depends(SupportService.init)],
):
    method = await support_service.handle_start(message)
    await bot(method)


@router.callback_query(
    ActionCallback.filter(F.action == Action.support_menu.action_name)
)
async def start_callback(
    callback_query: CallbackQuery,
    bot: Bot,
    support_service: Annotated[SupportService, Depends(SupportService.init)],
):
    method = await support_service.handle_start(callback_query)
    await bot(method)


@router.callback_query(
    SupportActionCallback.filter(F.action == Action.start_chat.action_name)
)
async def start_chat(
    callback_query: CallbackQuery,
    callback_data: SupportActionCallback,
    bot: Bot,
    support_service: Annotated[SupportService, Depends(SupportService.init)],
):
    method = await support_service.handle_chat_start(callback_query, callback_data)
    await bot(method)


@router.message(State(None), F.text)
async def handle_message(
    message: Message,
    bot: Bot,
    support_service: Annotated[SupportService, Depends(SupportService.init)],
):
    method = await support_service.handle_message(message)
    if method is not None:
        await bot(method)


@router.message(State(None), F.photo[-1].as_("image"))
async def handle_image(
    message: Message,
    image: PhotoSize,
    bot: Bot,
    support_service: Annotated[SupportService, Depends(SupportService.init)],
):
    file_info = await bot.get_file(message.photo[-1].file_id)
    method = await support_service.handle_image(message, image, file_info)
    if method is not None:
        await bot(method)

