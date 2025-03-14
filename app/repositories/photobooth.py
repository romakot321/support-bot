from aiohttp import ClientSession, BasicAuth
from loguru import logger
import os

from app.schemas.photobooth import PhotoBoothResponse, PhotoBoothUserSchema


class PhotoboothRepository:
    API_URL = os.getenv("PHOTOBOOTH_API_URL")

    async def get_user(self, telegram_id: int) -> PhotoBoothUserSchema:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.post(
                "/api/userInfo/" + str(telegram_id),
            )
            assert resp.status == 200, await resp.text()
            body = await resp.json()
        return PhotoBoothResponse.model_validate(body).data
