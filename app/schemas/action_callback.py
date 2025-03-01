from enum import Enum

from aiogram.filters.callback_data import CallbackData
from pydantic import Field, AliasChoices


class Action(Enum):
    support_category = dict(action_name='support_category', screen_name=None)
    support_done = dict(action_name='support_done', screen_name=None)
    support_invalid = dict(action_name='support_invalid', screen_name=None)

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
    subscription_cancel = "subscription_cancel"
    technical_issues = "technical_issues"
    generation_quality = "generation_quality"
    other = "other"


class SupportActionCallback(PaginatedActionCallback, prefix='support_action'):
    category: SupportCategory

