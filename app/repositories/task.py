from app.repositories.base import BaseRepository
from db.tables import Task


class TaskRepository[Table: Task, int](BaseRepository):
    base_table = Task

    async def create(self, **kwargs) -> Task:
        return await self._create(**kwargs)

    async def list(self, page=None, count=None) -> list[Task]:
        return await self._get_list(page=page, count=count)

    async def get(self, model_id: int) -> Task:
        return await self._get_one(id=model_id)

    async def update(self, model_id: int, **fields) -> Task:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

    async def count(self) -> int:
        return await self._count()

