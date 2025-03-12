from enum import Enum
import time
from email.utils import formatdate
import datetime as dt
import hmac
import os
import aiohttp
import json
import asyncio
import hashlib
import base64
import uuid

from loguru import logger
from pydantic import BaseModel
from sqlalchemy.util import b64encode


class CRMContact(BaseModel):
    id: int
    name: str
    account_id: int


class CRMStatus(BaseModel):
    id: int
    name: str


class CRMPipeline(BaseModel):
    class Attachment(BaseModel):
        statuses: list[CRMStatus]

    id: int
    name: str
    _embedded: Attachment


class CRMStatusId(Enum):
    subscription_cancel = 74563986
    technical_issues = 74563990
    generation_quality = 74563994
    other = 74563998
    success = 142


class CRMRepository:
    ACCESS_TOKEN = os.getenv("AMOCRM_ACCESS_TOKEN")
    SUBDOMAIN = os.getenv("AMOCRM_SUBDOMAIN")
    CHANNEL_SECRET = os.getenv("AMOCRM_CHANNEL_SECRET", "").encode()
    SCOPE_ID = os.getenv("AMOCRM_CHANNEL_SCOPE_ID")
    ACCOUNT_AMOJO_ID = os.getenv("AMOCRM_ACCOUNT_AMOJO_ID")

    def _load_tokens(self) -> dict | None:
        try:
            with open("tokens.json", "r") as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return None

    def _save_tokens(self, tokens: dict):
        with open("tokens.json", "w") as f:
            f.write(json.dumps(tokens))

    async def _post(
        self, path: str, json: list[dict] | dict, ignore_token: bool = False
    ) -> dict:
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.ACCESS_TOKEN}"},
            base_url=f"https://{self.SUBDOMAIN}.amocrm.ru",
        ) as session:
            response = await session.post(path, json=json)
            assert response.status == 200, await response.text()
            return (await response.json())["_embedded"]

    async def _get(self, path: str, params: dict) -> dict:
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.ACCESS_TOKEN}"},
            base_url=f"https://{self.SUBDOMAIN}.amocrm.ru",
        ) as session:
            response = await session.get(path, params=params)
            assert response.status == 200, await response.text()
            return (await response.json())

    async def add_contact(self, name: str, telegram_id: int) -> int:
        resp = await self._post(
            "/api/v4/contacts",
            json=[
                {
                    "name": name,
                    "custom_fields_values": [
                        {"field_id": 96497, "values": [{"value": str(telegram_id)}]}
                    ],
                }
            ],
        )
        return resp["contacts"][0]["id"]

    async def add_lead(self, contact_id: int, status: CRMStatusId) -> int:
        data = {
            "pipeline_id": 9295030,
            "status_id": status.value,
            "_embedded": {"contacts": [{"id": contact_id, "is_main": True}]},
        }
        resp = await self._post("/api/v4/leads", [data])
        return resp["leads"][0]["id"]

    async def update_lead(self, lead_id: int, status: CRMStatusId):
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.ACCESS_TOKEN}"},
            base_url=f"https://{self.SUBDOMAIN}.amocrm.ru",
        ) as session:
            response = await session.patch(
                "/api/v4/leads", json=[{"id": lead_id, "status_id": status.value}]
            )
            assert response.status == 200, await response.text()

    def _build_chat_auth_headers(
        self, request_method: str, request_path: str, request_body: bytes
    ) -> dict:
        date = dt.datetime.now()
        body_hash = hashlib.md5(request_body).hexdigest()

        headers = {
            "Content-MD5": body_hash,
            "Content-Type": "application/json",
            "Date": formatdate(time.mktime(date.timetuple())),
        }
        signature = "\n".join([request_method.upper()] + list(headers.values())) + "\n" + request_path
        headers["X-Signature"] = (
            hmac.new(self.CHANNEL_SECRET, signature.encode(), hashlib.sha1).hexdigest()
            .lower().rstrip("\n")
        )
        return headers

    async def create_chat(self, conversation_id: str, user_id: str, user_name: str) -> dict:
        body = json.dumps({"conversation_id": conversation_id, "user": {"id": user_id, "name": user_name}})
        path = f"/v2/origin/custom/{self.SCOPE_ID}/chats"
        auth_headers = self._build_chat_auth_headers("POST", path, body.encode())
        async with aiohttp.ClientSession(base_url="https://amojo.amocrm.ru", headers=auth_headers) as session:
            resp = await session.post(path, data=body)
            assert resp.status == 200, await resp.text()
            return await resp.json()

    async def user_send_message(self, conversation_id: str, user_id: str, user_name: str, message_text: str):
        data = {
            "event_type": "new_message",
            "payload": {
                "timestamp": int(time.time()),
                "msec_timestamp": int(time.time() * 1000),
                "conversation_id": conversation_id,
                "msgid": str(uuid.uuid4()),
                "sender": {"id": user_id, "name": user_name},
                "message": {
                    "type": "text",
                    "text": message_text
                }
            },
            "silent": False
        }
        body = json.dumps(data, indent=2)
        path = f"/v2/origin/custom/{self.SCOPE_ID}"
        auth_headers = self._build_chat_auth_headers("POST", path, body.encode())
        async with aiohttp.ClientSession(base_url="https://amojo.amocrm.ru", headers=auth_headers) as session:
            resp = await session.post(path, data=body)
            assert resp.status == 200, await resp.text()
            return await resp.json()

    async def attach_chat_contact(self, chat_id: str, contact_id: int):
        resp = await self._post("/api/v4/contacts/chats", json=[{"chat_id": chat_id, "contact_id": contact_id}])
        logger.debug(resp)

    async def __get_channel_account_amojo_id(self) -> str:
        response = await self._get("/api/v4/account", params={"with": "amojo_id"})
        return response["amojo_id"]

    async def __connect_account_to_channel(self, channel_id: str):
        account_id = await self.__get_channel_account_amojo_id()
        body = json.dumps({"account_id": account_id, "hook_api_version": "v2", "title": "PhotoBooth Support"})
        auth_headers = self._build_chat_auth_headers("POST", f'/v2/origin/custom/{channel_id}/connect', body.encode())
        async with aiohttp.ClientSession(base_url="https://amojo.amocrm.ru", headers=auth_headers) as session:
            resp = await session.post(f'/v2/origin/custom/{channel_id}/connect', data=body)
            print(await resp.text())


if __name__ == "__main__":
    import asyncio

    async def main():
        rep = CRMRepository()
        user_id = "703b82c0-4d0e-4444-8835-9491c6a11309"
        conv_id = "0fc59c07-6948-4166-8108-96f14fd8cb2f"
        chat = await rep.create_chat(conv_id, user_id, "Test")
        print(chat)
        msg = await rep.user_send_message(conv_id, user_id, "Test", "test message")
        print(msg)

    print(asyncio.run(main()))
