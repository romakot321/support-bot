import asyncio
import os

from yandex_cloud_ml_sdk import AsyncYCloudML


class LLMRepository:
    system_prompt = "Ты - служба поддержки сервиса по генерации изображений. Помоги пользователю с его проблемой."

    def __init__(self):
        sdk = AsyncYCloudML(
            folder_id=os.getenv("YANDEX_FOLDER_ID"),
            auth=os.getenv("YANDEX_KEY"),
        )
        self.model = sdk.models.completions("yandexgpt")

    @classmethod
    def init(cls):
        return cls()

    async def generate(self, prompt: str):
        operation = await self.model.configure(temperature=0.3).run_deferred(
            [
                {"role": "system", "text": self.system_prompt},
                {"role": "user", "text": prompt}
            ]
        )
        return await operation.wait(poll_interval=3)
