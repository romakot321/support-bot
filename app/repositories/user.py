from sqlalchemy import select
from app.repositories.base import BaseRepository
from db.tables import User


class UserRepository[Table: User, int](BaseRepository):
    base_table = User

    async def create(self, **kwargs) -> User:
        return await self._create(**kwargs)

    async def list(self, page=None, count=None) -> list[User]:
        return await self._get_list(page=page, count=count)

    async def get(self, model_id: int) -> User:
        return await self._get_one(id=model_id)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        query = select(self.base_table).filter_by(telegram_id=telegram_id)
        return await self.session.scalar(query)

    async def get_by_chat_id(self, chat_id: int) -> User | None:
        query = select(self.base_table).filter_by(current_chat_id=chat_id)
        return await self.session.scalar(query)

    async def update(self, model_id: int, **fields) -> User:
        return await self._update(model_id, **fields)

    async def delete(self, model_id: int):
        await self._delete(model_id)

    async def count(self) -> int:
        return await self._count()

