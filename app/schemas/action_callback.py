from enum import Enum

from aiogram.filters.callback_data import CallbackData
from pydantic import Field, AliasChoices


class Action(Enum):
    task_reload = dict(action_name='task_reload', screen_name='Обновить')
    task_start = dict(action_name='task_start', screen_name=None)

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


class TaskActionCallback(PaginatedActionCallback, prefix='task_action'):
    task_id: int = Field(validation_alias=AliasChoices('id', 'task_id'))

