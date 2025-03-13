from typing import Annotated

from aiogram import F
from aiogram import Router
from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram3_di import Depends

from app.schemas.action_callback import Action
from app.schemas.action_callback import ActionCallback
from app.schemas.subscription import SubscriptionChat
from app.services.subscription_category import SubscriptionCategoryService

router = Router(name=__name__)


@router.callback_query(
    ActionCallback.filter(F.action == Action.subscribtion_category.action_name)
)
async def menu(
    query: CallbackQuery,
    bot: Bot,
    category_service: Annotated[SubscriptionCategoryService, Depends(SubscriptionCategoryService.init)],
):
    method = await category_service.handle_menu(query)
    await bot(method)


@router.callback_query(
    ActionCallback.filter(F.action == Action.subscription_help.action_name)
)
async def subscription_help(
    query: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    category_service: Annotated[SubscriptionCategoryService, Depends(SubscriptionCategoryService.init)],
):
    method = await category_service.handle_subscription_help(query, state)
    await bot(method)


@router.message(SubscriptionChat.typing_first_message)
async def subscription_help_input(
    message: Message,
    bot: Bot,
    state: FSMContext,
    category_service: Annotated[SubscriptionCategoryService, Depends(SubscriptionCategoryService.init)],
):
    method = await category_service.handle_subscription_help_input(message, state)
    await bot(method)


@router.callback_query(
    ActionCallback.filter(F.action == Action.subscription_cancel_confirmation.action_name)
)
async def subscription_cancel_confirmation(
    query: CallbackQuery,
    bot: Bot,
    category_service: Annotated[SubscriptionCategoryService, Depends(SubscriptionCategoryService.init)],
):
    method = await category_service.handle_subscription_cancel_confirmation(query)
    await bot(method)


@router.callback_query(
    ActionCallback.filter(F.action == Action.subscription_cancel.action_name)
)
async def subscription_cancel(
    query: CallbackQuery,
    bot: Bot,
    category_service: Annotated[SubscriptionCategoryService, Depends(SubscriptionCategoryService.init)],
):
    method = await category_service.handle_subscription_cancel(query)
    await bot(method)
