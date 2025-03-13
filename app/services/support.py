import types
from typing import Annotated
from uuid import uuid4

from loguru import logger
from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types as am_types
from aiogram.methods import EditMessageText

from app.schemas.action_callback import (
    Action,
    SupportActionCallback,
    SupportCategory,
    ActionCallback,
)
from app.schemas.message import TextMessage
from app.schemas.texts import start_text, chat_started_text
from app.services.utils import build_aiogram_method
from app.repositories.crm import CRMRepository, CRMStatusId
from app.repositories.user import UserRepository
from app.repositories.llm import LLMRepository


class SupportService:
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
    def _build_support_status_keyboard(cls) -> am_types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=Action.subscribtion_category.screen_name,
            callback_data=ActionCallback(
                action=Action.subscribtion_category.action_name
            ),
        )
        builder.button(
            text=Action.payment_trable_category.screen_name,
            callback_data=ActionCallback(
                action=Action.payment_trable_category.action_name
            ),
        )
        builder.button(
            text=Action.picture_quality_category.screen_name,
            callback_data=ActionCallback(
                action=Action.picture_quality_category.action_name
            ),
        )
        builder.button(
            text=Action.other_category.screen_name,
            callback_data=ActionCallback(action=Action.other_category.action_name),
        )
        builder.adjust(1)
        return builder.as_markup()

    @classmethod
    def _build_answer_like_markup(cls) -> am_types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Вопрос решен",
            callback_data=ActionCallback(action=Action.support_done.action_name),
        )
        builder.button(
            text="Ответ не подходит",
            callback_data=ActionCallback(
                action=Action.support_invalid.action_name,
                category=SupportCategory.technical_issues,
            ),
        )
        builder.adjust(1)
        return builder.as_markup()

    @classmethod
    def _build_subcription_management_markup(cls) -> am_types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Отмена подписки",
            callback_data=ActionCallback(action=Action.support_done.action_name),
        )
        builder.button(
            text="Помощь с подпиской",
            callback_data=ActionCallback(
                action=Action.support_invalid.action_name,
                category=SupportCategory.technical_issues,
            ),
        )
        builder.adjust(1)
        return builder.as_markup()

    async def handle_start(self, msg: Message | CallbackQuery):
        user = await self.user_repository.get_by_telegram_id(msg.from_user.id)
        if user is None:
            crm_user_id = await self.crm_repository.add_contact(
                msg.from_user.username, msg.from_user.id
            )
            user = await self.user_repository.create(
                telegram_id=msg.from_user.id, crm_id=crm_user_id
            )
        elif user.current_chat_id is not None and user.crm_last_lead_id is not None:
            await self.crm_repository.update_lead(
                user.crm_last_lead_id, CRMStatusId.success
            )
            await self.user_repository.update(
                user.id,
                crm_last_lead_id=None,
                current_chat_id=None,
                current_chat_ref_id=None,
            )

        message = TextMessage(
            text=start_text,
            parse_mode="Markdownv2",
            reply_markup=self._build_support_status_keyboard(),
            message_id=(
                msg.message.message_id if isinstance(msg, CallbackQuery) else None
            ),
        )
        return build_aiogram_method(
            msg.from_user.id, message, use_edit=isinstance(msg, CallbackQuery)
        )

    async def handle_chat_start(
        self, query: CallbackQuery, callback_data: SupportActionCallback
    ):
        user = await self.user_repository.get_by_telegram_id(query.from_user.id)
        chat_id = str(uuid4())
        lead_id = await self.crm_repository.add_lead(
            user.crm_id, getattr(CRMStatusId, callback_data.category.value)
        )
        chat = await self.crm_repository.create_chat(
            chat_id, str(user.crm_id), str(user.id), query.from_user.full_name
        )
        logger.debug(f"Created {chat=}")
        await self.crm_repository.attach_chat_contact(chat["id"], user.crm_id)
        await self.user_repository.update(
            user.id,
            current_chat_id=chat_id,
            current_chat_ref_id=chat["id"],
            crm_last_lead_id=lead_id,
        )

        message = TextMessage(
            text=chat_started_text,
            parse_mode="Markdownv2",
            message_id=query.message.message_id,
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_message(self, message: Message):
        user = await self.user_repository.get_by_telegram_id(message.from_user.id)
        if user is None or user.current_chat_id is None:
            return
        await self.crm_repository.user_send_message(
            user.current_chat_id,
            user.current_chat_ref_id,
            str(user.crm_id),
            message.from_user.full_name,
            message.text,
        )

    async def handle_subcribe_category_choosed(self, query: CallbackQuery):
        message = TextMessage(
            text="Статус подписки", reply_markup=self._build_support_status_keyboard()
        )
        return build_aiogram_method(msg.from_user.id, message)

    async def handle_category_choosed(
        self, callback_data: SupportActionCallback, query: CallbackQuery
    ) -> EditMessageText:
        if callback_data.category == SupportCategory.subscription_cancel:
            return await self.handle_subcribe_category_choosed(query)
        status = getattr(CRMStatusId, callback_data.category.value)
        user = await self.user_repository.get_by_telegram_id(query.from_user.id)
        lead_id = await self.crm_repository.add_lead(user.crm_id, status)
        await self.user_repository.update(user.id, crm_last_lead_id=lead_id)
        message = TextMessage(
            text="Подробно опишите проблему, для максимально быстрого решения",
            reply_markup=None,
            message_id=query.message.message_id,
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
        await self.crm_repository.update_lead(
            user.crm_last_lead_id, CRMStatusId.success
        )
        message = TextMessage(
            text="Спасибо за обращение!", message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_failure(self, query: CallbackQuery):
        message = TextMessage(
            text="Пожалуйста, напишите менеджеру: t.me/id1",
            message_id=query.message.message_id,
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)
