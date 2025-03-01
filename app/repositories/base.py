from aiogram3_di import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_service import BaseService
from db import engine


class BaseRepository(BaseService):
    engine = engine

    @classmethod
    async def init(cls):
        async with cls() as self:
            yield self

