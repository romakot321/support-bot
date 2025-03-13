from enum import Enum

from aiogram.filters.callback_data import CallbackData
from pydantic import Field, AliasChoices


class Action(Enum):
    support_menu = dict(action_name='support_menu', screen_name="В меню 🔙")
    payment_trable_category = dict(action_name="payment_trable_category", screen_name="Проблемы с оплатой 💸")
    picture_quality_category = dict(action_name="picture_quality_category", screen_name="Качество фото 📸")
    other_category = dict(action_name="other_category", screen_name="Другое 🔎")
    subscribtion_category = dict(action_name="subscribtion_category", screen_name="Управление подпиской ✏️")
    subscription_cancel_confirmation = dict(action_name="subscription_cancel_confirmation", screen_name="Отмена подписки ❌")
    subscription_cancel = dict(action_name="subscription_cancel", screen_name="Отменить подписку")
    subscription_help = dict(action_name="subscription_help", screen_name="Помощь с подпиской ✅")
    start_chat = dict(action_name="start_chat", screen_name="Оператор 👩🏻‍💻")
    support_done = dict(action_name='support_done', screen_name=None)
    support_invalid = dict(action_name='support_invalid', screen_name=None)
    crm_message = dict(action_name="crm", screen_name=None)

    def __init__(self, values):
        self.action_name = values.get('action_name')
        self.screen_name = values.get('screen_name')


class ActionCallback(CallbackData, prefix='action'):
    """
    :param action: str, action_name from Action enum
    """
    action: str

    @classmethod
    def copy(cls):
        return cls(**cls.__dict__)

    def replace(self, **values):
        """Return new object with replaced values"""
        new_state = self.__dict__ | values
        return self.__class__(**new_state)


class PaginatedActionCallback(ActionCallback, prefix='paginated_action'):
    """
    :param page: int OR None, current page
    """
    page: int = 0


class SupportCategory(Enum):
    other = "other"
    payment = "payment"
    subscription = "subscription"
    picture = "picture"


class SupportActionCallback(PaginatedActionCallback, prefix='support_action'):
    category: SupportCategory


class ExternalActionCallback(PaginatedActionCallback, prefix='support_webhook'):
    chat_id: str  # conversation_id from AmoCRM

