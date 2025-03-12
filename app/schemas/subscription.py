from aiogram.fsm.state import State, StatesGroup


class SubscriptionChat(StatesGroup):
    typing_first_message = State()

