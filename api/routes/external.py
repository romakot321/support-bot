import hmac
import hashlib
import os
from fastapi import APIRouter, Depends, Request, HTTPException
from loguru import logger
from pydantic import BaseModel

from api.services.external import ExternalService, WebhookMessageSchema

router = APIRouter(prefix="/api/external", tags=["External"])
AMOCRM_CHANNEL_SECRET = os.getenv("AMOCRM_CHANNEL_SECRET", "").encode()


async def _authorize_amocrm_webhook(
        request: Request,
):
    signature = hmac.new(AMOCRM_CHANNEL_SECRET.encode(), await request.body(), digestmod=hashlib.sha256).digest()
    if signature.decode() != request.headers["X-Signature"]:
        logger.debug(("invalid signature", request.headers, signature))
        raise HTTPException(401)


@router.post("/webhook", dependencies=[Depends(_authorize_amocrm_webhook)])
async def handle_webhook(
    schema: WebhookMessageSchema,
    service: ExternalService = Depends()
):
    await service.handle(schema)
