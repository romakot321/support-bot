from typing import Annotated

from aiogram import F
from aiogram import Router
from aiogram import Bot
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram3_di import Depends

from app.schemas.action_callback import Action, TaskActionCallback
from app.schemas.action_callback import ActionCallback
from app.services.task import TaskService

router = Router(name=__name__)


@router.message(CommandStart())
async def start_command(
        message: Message,
        bot: Bot,
        task_service: Annotated[
            TaskService, Depends(TaskService.init)]
):
    return await task_service.handle_task_create(message, bot)


@router.callback_query(
    ActionCallback.filter(
        F.action == Action.task_reload.action_name
    )
)
async def task_reload_callback(
        query: CallbackQuery,
        bot: Bot,
        callback_data: TaskActionCallback,
        task_service: Annotated[
            TaskService, Depends(TaskService.init)]
):
    await bot(await task_service.handle_task_reload(callback_data, query))


@router.callback_query(
    ActionCallback.filter(
        F.action == Action.task_start.action_name
    )
)
async def task_start_callback(
        query: CallbackQuery,
        bot: Bot,
        callback_data: TaskActionCallback,
        task_service: Annotated[
            TaskService, Depends(TaskService.init)]
):
    pass

