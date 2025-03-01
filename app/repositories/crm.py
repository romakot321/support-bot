from enum import Enum
import os
import aiohttp
import json
import asyncio

from pydantic import BaseModel


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

    def _load_tokens(self) -> dict | None:
        try:
            with open("tokens.json", "r") as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return None

    def _save_tokens(self, tokens: dict):
        with open("tokens.json", "w") as f:
            f.write(json.dumps(tokens))

    async def _post(self, path: str, json: list[dict] | dict, ignore_token: bool = False) -> dict:
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.ACCESS_TOKEN}"},
            base_url=f"https://{self.SUBDOMAIN}.amocrm.ru",
        ) as session:
            response = await session.post(path, json=json)
            assert response.status == 200, await response.text()
            return (await response.json())["_embedded"]

    async def _get(self, path: str, params: dict) -> dict:
        async with aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.access_token}"},
            base_url=f"https://{self.SUBDOMAIN}.amocrm.ru",
        ) as session:
            response = await session.get(path, params=params)
            assert response.status == 200, await response.text()
            return (await response.json())["_embedded"]

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
            response = await session.patch("/api/v4/leads", json=[{"id": lead_id, "status_id": status.value}])
            assert response.status == 200, await response.text()
