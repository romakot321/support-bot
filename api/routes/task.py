from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from api.services.task import TaskService

router = APIRouter(prefix="/api/task", tags=["Task"])


@router.post("/{task_id}")
async def start_task(
        task_id: int,
        service: TaskService = Depends()
):
    return await service.start(task_id)

