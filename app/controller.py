from fastapi import Depends
from aiogram.filters.callback_data import CallbackData
import app
import copy
import json
import asyncio

from app.schemas.action_callback import Action, ExternalActionCallback


class BotController:
    __webhook_data = {
        'update_id': 0,
        'callback_query': {
            'id': '1',
            'from': {
                'id': None,
                'is_bot': False,
                'first_name': '.'
            },
            'message': {
                'message_id': 1,
                'from': {
                    'id': 1,
                    'is_bot': True,
                    'first_name': "bot"
                },
                'chat': {
                    'id': None,
                    'first_name': '.',
                    'type': 'private'
                },
                'date': 1,
                'text': '.'
            },
            'data': 'action:history',
            'chat_instance': '1'
        }
    }

    @staticmethod
    def _parse_webhook(data) -> str:
        return ExternalActionCallback(
            action=Action.crm_message.action_name,
            chat_id=data.message.conversation.client_id
        ).pack()

    @classmethod
    def _pack_webhook_data(cls, chat_id: int, data: str) -> str:
        webhookdata = copy.deepcopy(cls.__webhook_data)
        webhookdata['callback_query']['from']['id'] = chat_id
        webhookdata['callback_query']['message']['chat']['id'] = chat_id
        webhookdata['callback_query']['data'] = data
        return json.dumps(webhookdata)

    @classmethod
    async def handle_crm_webhook(cls, data):
        packed_data = cls._parse_webhook(data)
        webhookdata = copy.deepcopy(cls.__webhook_data)
        webhookdata['callback_query']['from']['id'] = 0
        webhookdata['callback_query']['message']['chat']['id'] = 0
        webhookdata['callback_query']['message']['text'] = data.message.message.text
        webhookdata['callback_query']['data'] = packed_data

        asyncio.create_task(app.dispatcher_instance.feed_webhook_update(
            app.bot_instance, app.bot_instance.session.json_loads(json.dumps(webhookdata))
        ))

