from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData
from typing import Optional
from enum import Enum


class Action(str, Enum):
    send_from_user = "user"
    send_from_supp = "support"


class CallbackFactory(CallbackData, prefix="callback"):
    action: Action
    id: Optional[int | str]


class Form(StatesGroup):
    user_to_user = State()
    user_to_support = State()
    support_to_user = State()
