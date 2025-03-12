from fastapi import Depends
from pydantic import BaseModel

from app.controller import BotController


class WebhookMessageSchema(BaseModel):
    class Message(BaseModel):
        class Conversation(BaseModel):
            id: str
            client_id: str

        class MessageMessage(BaseModel):
            type: str
            text: str

        conversation: Conversation
        message: MessageMessage

    account_id: str
    message: Message


class ExternalService:
    def __init__(self, bot_controller: BotController = Depends()):
        self.bot_controller = bot_controller

    async def handle(self, schema: WebhookMessageSchema):
        await self.bot_controller.handle_crm_webhook(schema)

