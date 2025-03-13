from typing import Annotated
from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types as types
from aiogram.methods import EditMessageText
from aiogram.fsm.context import FSMContext

from app.schemas.texts import picture_faq_text
from app.schemas.action_callback import (
    Action,
    ActionCallback,
    SupportActionCallback,
    SupportCategory,
)
from app.schemas.message import TextMessage
from app.services.utils import build_aiogram_method
from app.repositories.user import UserRepository
from app.repositories.llm import LLMRepository
from app.repositories.crm import CRMRepository


class PictureCategoryService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(UserRepository.init)],
        crm_repository: CRMRepository,
        llm_repository: LLMRepository,
    ):
        self.user_repository = user_repository
        self.crm_repository = crm_repository
        self.llm_repository = llm_repository

    @classmethod
    def init(
        cls, user_repository: Annotated[UserRepository, Depends(UserRepository.init)]
    ):
        return cls(
            user_repository=user_repository,
            crm_repository=CRMRepository(),
            llm_repository=LLMRepository(),
        )

    @classmethod
    def _build_picture_keyboard(cls) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Спасибо 💚",
            url="https://t.me/fotobudka_ai_bot",
        )
        builder.button(
            text=Action.start_chat.screen_name,
            callback_data=SupportActionCallback(
                action=Action.start_chat.action_name, category=SupportCategory.picture
            ),
        )
        builder.adjust(1)
        return builder.as_markup()

    async def handle_menu(self, query: CallbackQuery):
        message = TextMessage(
            text=picture_faq_text,
            reply_markup=self._build_picture_keyboard(),
            parse_mode="Markdownv2",
            message_id=query.message.message_id,
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)
