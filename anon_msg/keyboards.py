import text
from states import Action, CallbackFactory
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=text.cancel)]],
    resize_keyboard=True,
)


def profile_kb(user_id: int) -> InlineKeyboardMarkup:
    btn = InlineKeyboardButton(text=text.profile, url=f"tg://user?id={user_id}")
    return InlineKeyboardMarkup(inline_keyboard=[[btn]])


def answer_kb(
    to_whom_id: int, replay: bool = False, supp: bool = False
) -> InlineKeyboardMarkup:
    anon_btn_data = CallbackFactory(action=Action.send_from_user, id=to_whom_id).pack()
    anon_btn_text = text.send_more if replay else text.answer
    anon_btn = InlineKeyboardButton(text=anon_btn_text, callback_data=anon_btn_data)
    if not supp:
        return InlineKeyboardMarkup(inline_keyboard=[[anon_btn]])
    supp_btn_data = CallbackFactory(action=Action.send_from_supp, id=to_whom_id).pack()
    supp_btn_text = text.answer_as_supp
    supp_btn = InlineKeyboardButton(text=supp_btn_text, callback_data=supp_btn_data)
    return InlineKeyboardMarkup(inline_keyboard=[[anon_btn, supp_btn]])
