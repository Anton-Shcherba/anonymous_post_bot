import config, text
import asyncio
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ErrorEvent,
)
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from enum import Enum


form_router = Router()


class Form(StatesGroup):
    user_to_user = State()
    user_to_support = State()
    support_to_user = State()


class Action(str, Enum):
    send_from_user = "user"
    send_from_supp = "support"


class CallbackFactory(CallbackData, prefix="callback"):
    action: Action
    id: Optional[int | str]


def answer_keyboard(
    to_whom_id: int, replay: bool = False, support: bool = False
) -> InlineKeyboardMarkup:
    anon_btn_data = CallbackFactory(action=Action.send_from_user, id=to_whom_id).pack()
    anon_btn_text = text.send_more if replay else text.answer
    anon_btn = InlineKeyboardButton(text=anon_btn_text, callback_data=anon_btn_data)
    if not support:
        return InlineKeyboardMarkup(inline_keyboard=[[anon_btn]])
    supp_btn_data = CallbackFactory(action=Action.send_from_supp, id=to_whom_id).pack()
    supp_btn_text = text.answer_as_supp
    supp_btn = InlineKeyboardButton(text=supp_btn_text, callback_data=supp_btn_data)
    return InlineKeyboardMarkup(inline_keyboard=[[anon_btn], [supp_btn]])


def cancel_keyboard() -> ReplyKeyboardMarkup:
    button = KeyboardButton(text=text.cancel)
    return ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)


def profile_keyboard(user_id: int) -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(text=text.profile, url=f"tg://user?id={user_id}")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


async def send_link(message: Message, state: FSMContext) -> None:
    await state.clear()
    start_link_msg = text.start_msg_tmpl.format(id=message.from_user.id)
    await message.answer(start_link_msg, reply_markup=ReplyKeyboardRemove())


@form_router.message(CommandStart())
async def cmd_start_handler(
    message: Message, state: FSMContext, command: CommandObject
) -> None:
    match command.args:
        case None:
            await send_link(message, state)
        case str(message.from_user.id):
            await state.clear()
            await message.answer(text.to_myself_err, reply_markup=ReplyKeyboardRemove())
        case _:
            await state.set_state(Form.user_to_user)
            await state.update_data(user_to_user=command.args)
            await message.answer(text.send_msg, reply_markup=cancel_keyboard())


@form_router.callback_query(CallbackFactory.filter(F.action == Action.send_from_user))
async def cb_from_user_handler(
    callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
) -> None:
    await callback.answer()
    await state.set_state(Form.user_to_user)
    await state.update_data(user_to_user=callback_data.id)
    await callback.message.answer(text.send_msg, reply_markup=cancel_keyboard())


@form_router.callback_query(CallbackFactory.filter(F.action == Action.send_from_supp))
async def cb_from_support_handler(
    callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
) -> None:
    await callback.answer()
    await state.set_state(Form.support_to_user)
    await state.update_data(support_to_user=callback_data.id)
    await callback.message.answer(text.send_from_supp, reply_markup=cancel_keyboard())


@form_router.message(Command("cancel"))
@form_router.message(F.text == text.cancel)
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text.cancel_msg, reply_markup=ReplyKeyboardRemove())


@form_router.message(Command("support"))
async def cmd_support_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.user_to_support)
    await message.answer(text.send_to_supp, reply_markup=cancel_keyboard())


async def state_parse(state: FSMContext) -> tuple[str, bool, bool, bool]:
    current_state = await state.get_state()
    data = await state.get_data()
    match current_state:
        case Form.user_to_user:
            for_admin = id == config.ADMIN_ID
            return (data.get(Form.user_to_user._state), for_admin, False, False)
        case Form.user_to_support:
            return (config.ADMIN_ID, True, True, False)
        case Form.support_to_user:
            return (data.get(Form.support_to_user._state), False, False, True)


@form_router.message(~StateFilter(None))
async def state_handler(message: Message, state: FSMContext) -> None:
    to_whom_id, for_admin, for_spt, from_spt = await state_parse(state)
    from_whom_id = message.from_user.id
    await state.clear()

    msg_txt = text.msg_recv_spt if for_spt or from_spt else text.msg_recv
    msg_txt += text.id_link_tmpl.format(id=message.from_user.id) if for_admin else ""
    new_msg_kb = profile_keyboard(from_whom_id) if for_admin else None
    await message.bot.send_message(to_whom_id, msg_txt, reply_markup=new_msg_kb)

    copy_msg_kb = None if from_spt else answer_keyboard(from_whom_id, support=for_admin)
    await message.copy_to(to_whom_id, reply_markup=copy_msg_kb)

    await message.answer(text.msg_sent, reply_markup=ReplyKeyboardRemove())

    if not (for_spt or from_spt):
        one_more_kb = answer_keyboard(to_whom_id, True)
        await message.answer(text.one_more_msg, reply_markup=one_more_kb)


@form_router.message()
async def other_msg_handler(message: Message, state: FSMContext) -> None:
    await send_link(message, state)


@form_router.error(F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text.any_err, reply_markup=ReplyKeyboardRemove())


async def main():
    bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
