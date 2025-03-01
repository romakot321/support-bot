import types
from typing import Annotated
from aiogram3_di import Depends

from aiogram import Bot
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types as am_types
from aiogram.methods import EditMessageText

from app.repositories.task import TaskRepository
from app.schemas.action_callback import Action, TaskActionCallback
from app.schemas.message import TextMessage
from app.services.utils import build_aiogram_method


class TaskService:
    def __init__(self, task_repository: Annotated[TaskRepository, Depends(TaskRepository.init)]):
        self.task_repository = task_repository

    @classmethod
    def init(cls, task_repository: Annotated[TaskRepository, Depends(TaskRepository.init)]):
        return cls(task_repository=task_repository)

    @classmethod
    def _build_task_status_keyboard(cls, task_id: int) -> am_types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(
            text="Обновить",
            callback_data=TaskActionCallback(action=Action.task_reload.action_name, task_id=task_id)
        )
        builder.adjust(1)
        return builder.as_markup()

    async def handle_task_create(self, msg: Message, bot: Bot):
        model = await self.task_repository.create(user_id=msg.from_user.id)
        message = TextMessage(
            text=f"Задача {model.id} создана",
            reply_markup=self._build_task_status_keyboard(model.id)
        )
        method = build_aiogram_method(msg.from_user.id, message)

        response = await bot(method)
        await self.task_repository.update(model.id, message_id=response.message.id)

    async def handle_task_reload(self, callback_data: TaskActionCallback, query: CallbackQuery) -> EditMessageText:
        model = await self.task_repository.get(callback_data.task_id)
        message = TextMessage(
            text="Задача в процессе",
            reply_markup=self._build_task_status_keyboard(model.id),
            message_id=model.id
        )
        return build_aiogram_method(query.from_user.id, message, use_edit=True)
