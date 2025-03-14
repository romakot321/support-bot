from operator import call
from typing import Annotated
from uuid import uuid4

from loguru import logger
from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types as types
from aiogram.methods import EditMessageText
from aiogram.fsm.context import FSMContext

from app.repositories.cloudpayments import CloudpaymentsRepository
from app.repositories.photobooth import PhotoboothRepository
from app.schemas.subscription import SubscriptionChat
from app.schemas.texts import (
    subscription_cancel_confirmation_text,
    subscription_help_text,
)
from app.schemas.texts import subscription_chat_started_text, subscription_cancel_text
from app.schemas.action_callback import Action, ActionCallback
from app.schemas.message import TextMessage
from app.services.utils import build_aiogram_method
from app.repositories.crm import CRMRepository, CRMStatusId
from app.repositories.user import UserRepository


class SubscriptionCategoryService:
    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends(UserRepository.init)],
        crm_repository: CRMRepository,
        photobooth_repository: PhotoboothRepository,
        cloudpayments_repository: CloudpaymentsRepository,
    ):
        self.user_repository = user_repository
        self.crm_repository = crm_repository
        self.photobooth_repository = photobooth_repository
        self.cloudpayments_repository = cloudpayments_repository

    @classmethod
    def init(
        cls, user_repository: Annotated[UserRepository, Depends(UserRepository.init)]
    ):
        return cls(
            user_repository=user_repository,
            crm_repository=CRMRepository(),
            photobooth_repository=PhotoboothRepository(),
            cloudpayments_repository=CloudpaymentsRepository(),
        )

    @classmethod
    def _build_subscription_confirmation_keyboard(cls) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=Action.subscription_cancel.screen_name,
            callback_data=ActionCallback(action=Action.subscription_cancel.action_name),
        )
        builder.button(
            text=Action.support_menu.screen_name,
            callback_data=ActionCallback(action=Action.support_menu.action_name),
        )
        builder.adjust(1)
        return builder.as_markup()

    @classmethod
    def _build_subscription_keyboard(cls) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=Action.subscription_cancel_confirmation.screen_name,
            callback_data=ActionCallback(
                action=Action.subscription_cancel_confirmation.action_name
            ),
        )
        builder.button(
            text=Action.subscription_help.screen_name,
            callback_data=ActionCallback(action=Action.subscription_help.action_name),
        )
        builder.button(
            text=Action.support_menu.screen_name,
            callback_data=ActionCallback(action=Action.support_menu.action_name),
        )
        builder.adjust(1)
        return builder.as_markup()

    async def _create_crm_chat(self, query: CallbackQuery):
        user = await self.user_repository.get_by_telegram_id(query.from_user.id)
        chat_id = str(uuid4())
        lead = await self.crm_repository.add_lead(user.crm_id, CRMStatusId.subscription)
        chat = await self.crm_repository.create_chat(
            chat_id, str(user.crm_id), str(user.id), query.from_user.full_name
        )
        logger.debug(f"Created {chat=}")
        await self.crm_repository.attach_chat_contact(chat["id"], user.crm_id)
        await self.user_repository.update(
            user.id, current_chat_id=chat_id, current_chat_ref_id=chat["id"]
        )

    async def handle_menu(self, query: CallbackQuery):
        user_info = await self.photobooth_repository.get_user(query.from_user.id)
        message = TextMessage(
            text="Ваша подписка активна"
            if user_info.hasSubscription
            else "Ваша подписка неактивна",
            reply_markup=self._build_subscription_keyboard(),
            message_id=query.message.message_id,
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_subscription_help(
        self, query: CallbackQuery, fsm_context: FSMContext
    ):
        await fsm_context.set_state(SubscriptionChat.typing_first_message)
        await self._create_crm_chat(query)
        message = TextMessage(
            text=subscription_help_text, message_id=query.message.message_id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_subscription_help_input(
        self, msg: Message, fsm_context: FSMContext
    ):
        await fsm_context.clear()
        user = await self.user_repository.get_by_telegram_id(msg.from_user.id)

        await self.crm_repository.user_send_message(
            user.current_chat_id,
            user.current_chat_ref_id,
            str(user.crm_id),
            msg.from_user.full_name,
            msg.text,
        )

        message = TextMessage(text=subscription_chat_started_text)
        return build_aiogram_method(msg.from_user.id, message)

    async def handle_subscription_cancel_confirmation(self, query: CallbackQuery):
        message = TextMessage(
            text=subscription_cancel_confirmation_text,
            parse_mode="MarkdownV2",
            reply_markup=self._build_subscription_confirmation_keyboard(),
            message_id=query.message.message_id,
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)

    async def handle_subscription_cancel(self, query: CallbackQuery):
        await self._create_crm_chat(query)
        chatid = query.from_user.id

        user_info = await self.photobooth_repository.get_user(chatid)
        if user_info.subscriptionId is None:
            message = TextMessage(
                text="У вас нет активноай подписки",
                reply_markup=self._build_subscription_keyboard(),
                message_id=query.message.message_id,
            )
            return build_aiogram_method(query.from_user.id, message, use_edit=True)

        await self.cloudpayments_repository.cancel_subscription(
            user_info.subscriptionId
        )

        message = TextMessage(
            text=subscription_cancel_text,
            parse_mode="MarkdownV2",
            message_id=query.message.message_id,
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text="10 фото",
                            web_app=types.WebAppInfo(
                                url=f"https://bot.fotobudka.online/api/userPayment/{chatid}/buy10photo/1"
                            ),
                        ),
                        types.InlineKeyboardButton(
                            text="50 фото",
                            web_app=types.WebAppInfo(
                                url=f"https://bot.fotobudka.online/api/userPayment/{chatid}/buy50photo/1"
                            ),
                        ),
                        types.InlineKeyboardButton(
                            text="100 фото",
                            web_app=types.WebAppInfo(
                                url=f"https://bot.fotobudka.online/api/userPayment/{chatid}/buy100photo/1"
                            ),
                        ),
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="300 фото",
                            web_app=types.WebAppInfo(
                                url=f"https://bot.fotobudka.online/api/userPayment/{chatid}/buy300photo/1"
                            ),
                        ),
                        types.InlineKeyboardButton(
                            text="500 фото",
                            web_app=types.WebAppInfo(
                                url=f"https://bot.fotobudka.online/api/userPayment/{chatid}/buy500photo/1"
                            ),
                        ),
                        types.InlineKeyboardButton(
                            text="1000 фото",
                            web_app=types.WebAppInfo(
                                url=f"https://bot.fotobudka.online/api/userPayment/{chatid}/buy1000photo/1"
                            ),
                        ),
                    ],
                    [
                        types.InlineKeyboardButton(
                            text=Action.support_menu.screen_name,
                            callback_data=ActionCallback(
                                action=Action.support_menu.action_name
                            ).pack(),
                        )
                    ],
                ]
            ),
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)
