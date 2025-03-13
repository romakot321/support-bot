from aiohttp import ClientSession, BasicAuth
from loguru import logger
import os


class CloudpaymentsRepository:
    API_URL = "https://api.cloudpayments.ru"
    API_SECRET = os.getenv("CLOUDPAYMENTS_API_TOKEN")
    API_PUBLIC_ID = os.getenv("CLOUDPAYMENTS_API_PUBLIC_ID")

    async def cancel_subscription(self, subscription_id: str) -> bool:
        async with ClientSession(base_url=self.API_URL) as session:
            resp = await session.post(
                "/subscriptions/cancel",
                json={"Id": subscription_id},
                auth=BasicAuth(self.API_PUBLIC_ID, self.API_SECRET),
            )
            assert resp.status == 200, await resp.text()
            body = await resp.json()
        logger.debug(body)
        return body["Success"]
