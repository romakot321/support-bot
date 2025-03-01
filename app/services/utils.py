from aiogram.methods import EditMessageText, EditMessageMedia
from aiogram.methods import SendMessage, SendDocument, SendMediaGroup

from app.schemas.message import TextMessage, MediaMessage, MediaGroupMessage

__message_type_to_send_method: dict = {
    TextMessage: SendMessage,
    MediaMessage: SendDocument,
    MediaGroupMessage: SendMediaGroup
}
__message_type_to_edit_method: dict = {
    TextMessage: EditMessageText,
    MediaMessage: EditMessageMedia
}


def build_aiogram_method(
        telegram_id,
        message: TextMessage | MediaMessage,
        use_edit: bool = False,
) -> SendMessage | SendDocument | None:
    """Return None if unknown message type"""
    if use_edit:
        method = __message_type_to_edit_method.get(type(message))
    else:
        method = __message_type_to_send_method.get(type(message))
    if method is None:
        raise ValueError("Unknown message type")
    return method(chat_id=telegram_id, **message.model_dump())
