from typing import Annotated

from aiogram import F
from aiogram import Router
from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.state import State
from aiogram3_di import Depends

from app.schemas.action_callback import Action, ExternalActionCallback
from app.schemas.action_callback import ActionCallback
from app.services.external import ExternalService

router = Router(name=__name__)


@router.callback_query(
    ExternalActionCallback.filter(F.action == Action.crm_message.action_name)
)
async def message_callback(
    callback_query: CallbackQuery,
    callback_data: ExternalActionCallback,
    bot: Bot,
    external_service: Annotated[ExternalService, Depends(ExternalService.init)],
):
    method = await external_service.handle_message(callback_query, callback_data)
    if method:
        await bot(method)
