import types
from typing import Annotated
from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types as am_types
from aiogram.methods import EditMessageText

from app.schemas.action_callback import Action, SupportActionCallback, SupportCategory, ActionCallback
from app.schemas.message import TextMessage
from app.services.utils import build_aiogram_method
from app.repositories.crm import CRMRepository, CRMStatusId
from app.repositories.user import UserRepository
from app.repositories.llm import LLMRepository


class SupportService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends(UserRepository.init)],
            crm_repository: CRMRepository,
            llm_repository: LLMRepository
    ):
        self.user_repository = user_repository
        self.crm_repository = crm_repository
        self.llm_repository = llm_repository

    @classmethod
    def init(cls, user_repository: Annotated[UserRepository, Depends(UserRepository.init)]):
        return cls(
            user_repository=user_repository,
            crm_repository=CRMRepository(),
            llm_repository=LLMRepository()
        )

    @classmethod
    def _build_support_status_keyboard(cls) -> am_types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Отмена подписки",
            callback_data=SupportActionCallback(action=Action.support_category.action_name, category=SupportCategory.subscription_cancel)
        )
        builder.button(
            text="Оплата",
            callback_data=SupportActionCallback(action=Action.support_category.action_name, category=SupportCategory.technical_issues)
        )
        builder.button(
            text="Качество генераций",
            callback_data=SupportActionCallback(action=Action.support_category.action_name, category=SupportCategory.generation_quality)
        )
        builder.button(
            text="Другое",
            callback_data=SupportActionCallback(action=Action.support_category.action_name, category=SupportCategory.other)
        )
        builder.adjust(1)
        return builder.as_markup()

    @classmethod
    def _build_answer_like_markup(cls) -> am_types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Вопрос решен",
            callback_data=ActionCallback(action=Action.support_done.action_name)
        )
        builder.button(
            text="Ответ не подходит",
            callback_data=ActionCallback(action=Action.support_invalid.action_name, category=SupportCategory.technical_issues)
        )
        builder.adjust(1)
        return builder.as_markup()

    async def handle_start(self, msg: Message):
        user = await self.user_repository.get_by_telegram_id(msg.from_user.id)
        if user is None:
            crm_user_id = await self.crm_repository.add_contact(msg.from_user.username, msg.from_user.id)
            user = await self.user_repository.create(telegram_id=msg.from_user.id, crm_id=crm_user_id)

        message = TextMessage(
            text=f"Добро пожаловать в службу поддержки Фотобудки, выберите категорию обращения",
            reply_markup=self._build_support_status_keyboard()
        )
        return build_aiogram_method(msg.from_user.id, message)

    async def handle_category_choosed(self, callback_data: SupportActionCallback, query: CallbackQuery) -> EditMessageText:
        status = getattr(CRMStatusId, callback_data.category.value)
        user = await self.user_repository.get_by_telegram_id(query.from_user.id)
        lead_id = await self.crm_repository.add_lead(user.crm_id, status)
        await self.user_repository.update(user.id, crm_last_lead_id=lead_id)
        message = TextMessage(
            text="Подробно опишите проблему, для максимально быстрого решения",
            reply_markup=None,
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def answer(self, msg: Message):
        user = await self.user_repository.get_by_telegram_id(msg.from_user.id)
        if user.crm_last_lead_id is None:
            return
        text = await self.llm_repository.generate(msg.text)
        message = TextMessage(
            text=text,
            reply_markup=self._build_answer_like_markup(),
        )
        return build_aiogram_method(msg.from_user.id, message)

    async def handle_success(self, query: CallbackQuery):
        user = await self.user_repository.get_by_telegram_id(query.from_user.id)
        await self.crm_repository.update_lead(user.crm_last_lead_id, CRMStatusId.success)
        message = TextMessage(
            text="Спасибо за обращение!",
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_failure(self, query: CallbackQuery):
        message = TextMessage(
            text="Пожалуйста, напишите менеджеру: t.me/id1",
            message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

