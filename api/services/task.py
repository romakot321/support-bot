from fastapi import Depends

from app.controller import BotController


class TaskService:
    def __init__(self, bot_controller: BotController = Depends()):
        self.bot_controller = bot_controller

    async def start(self, task_id: int):
        await self.bot_controller.start_task(task_id)

