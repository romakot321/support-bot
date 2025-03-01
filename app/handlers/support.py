from typing import Annotated

from aiogram import F
from aiogram import Router
from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message
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
    SupportActionCallback.filter(F.action == Action.support_category.action_name)
)
async def category_choose(
    query: CallbackQuery,
    bot: Bot,
    callback_data: SupportActionCallback,
    support_service: Annotated[SupportService, Depends(SupportService.init)],
):
    method = await support_service.handle_category_choosed(callback_data, query)
    await bot(method)


@router.message(F.text)
async def process_text(
    message: Message,
    bot: Bot,
    support_service: Annotated[SupportService, Depends(SupportService.init)],
):
    method = await support_service.answer(message)
    if method is not None:
        await bot(method)


@router.callback_query(
    ActionCallback.filter(F.action == Action.support_done.action_name)
)
async def support_done(
    query: CallbackQuery,
    bot: Bot,
    callback_data: SupportActionCallback,
    support_service: Annotated[SupportService, Depends(SupportService.init)],
):
    method = await support_service.handle_success(query)
    await bot(method)


@router.callback_query(
    ActionCallback.filter(F.action == Action.support_invalid.action_name)
)
async def support_failure(
    query: CallbackQuery,
    bot: Bot,
    callback_data: SupportActionCallback,
    support_service: Annotated[SupportService, Depends(SupportService.init)],
):
    method = await support_service.handle_failure(query)
    await bot(method)
