from typing import Annotated
from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types as types
from aiogram.methods import EditMessageText
from aiogram.fsm.context import FSMContext

from app.schemas.action_callback import Action, ActionCallback, ExternalActionCallback
from app.schemas.message import TextMessage
from app.services.utils import build_aiogram_method
from app.repositories.user import UserRepository
from app.repositories.crm import CRMRepository


class ExternalService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(UserRepository.init)],
        crm_repository: CRMRepository,
    ):
        self.user_repository = user_repository
        self.crm_repository = crm_repository

    @classmethod
    def init(
        cls, user_repository: Annotated[UserRepository, Depends(UserRepository.init)]
    ):
        return cls(
            user_repository=user_repository,
            crm_repository=CRMRepository(),
        )

    async def handle_message(self, query: CallbackQuery, data: ExternalActionCallback):
        user = await self.user_repository.get_by_chat_id(data.chat_id)
        if user is None:
            return
        message = TextMessage(
            text=query.message.text,
        )
        return build_aiogram_method(user.telegram_id, message)

