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
from app.services.other_category import OtherCategoryService

router = Router(name=__name__)


@router.callback_query(
    ActionCallback.filter(F.action == Action.other_category.action_name)
)
async def menu(
    query: CallbackQuery,
    bot: Bot,
    category_service: Annotated[
        OtherCategoryService, Depends(OtherCategoryService.init)
    ],
):
    method = await category_service.handle_menu(query)
    await bot(method)
