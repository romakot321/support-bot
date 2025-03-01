from aiogram import types
from pydantic import BaseModel, ConfigDict, computed_field, Field


class Message(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    message_id: int | None = None  # message_id used for edit, get it from telegram response


class TextMessage(Message):
    text: str
    reply_markup: types.InlineKeyboardMarkup | None = None
    parse_mode: str | None = None


class MediaMessage(Message):
    caption: str | None = None
    document: types.BufferedInputFile
    reply_markup: types.InlineKeyboardMarkup | None = None
    parse_mode: str | None = None

    @computed_field
    @property
    def media(self) -> types.InputMediaDocument:
        return types.InputMediaDocument(media=self.document, caption=self.caption, parse_mode=self.parse_mode)


class MediaGroupMessage(Message):
    caption: str | None = None
    files_: list[bytes] = Field(validation_alias='files')
    parse_mode: str | None = None
    reply_markup: types.InlineKeyboardMarkup | None = None

    @computed_field
    @property
    def media(self) -> list[types.InputMediaPhoto]:
        if not self.files_:
            return []
        media = [
            types.InputMediaDocument(
                media=types.BufferedInputFile(self.files_[0], filename='file'),
                caption=self.caption,
                parse_mode=self.parse_mode
            )
        ]
        return media + [
            types.InputMediaDocument(media=types.BufferedInputFile(file, filename='file'))
            for file in self.files_[1:]
        ]

