import config
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
    User,
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
    anon_btn_text = "🔄 Отправить ещё" if replay else "🔄 Ответить"
    anon_btn = InlineKeyboardButton(text=anon_btn_text, callback_data=anon_btn_data)
    if not support:
        return InlineKeyboardMarkup(inline_keyboard=[[anon_btn]])
    supp_btn_data = CallbackFactory(action=Action.send_from_supp, id=to_whom_id).pack()
    supp_btn_text = "⚠️ Ответить"
    supp_btn = InlineKeyboardButton(text=supp_btn_text, callback_data=supp_btn_data)
    return InlineKeyboardMarkup(inline_keyboard=[[anon_btn], [supp_btn]])


def cancel_keyboard() -> ReplyKeyboardMarkup:
    button = KeyboardButton(text="♻️ Отмена")
    return ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)


def profile_keyboard(user_id: int) -> InlineKeyboardMarkup:
    button = InlineKeyboardButton(text="👤 Профиль", url=f"tg://user?id={user_id}")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])


async def send_link(message: Message, state: FSMContext) -> None:
    await state.clear()
    template = "🔗 Вот твоя личная ссылка, опубликуй её и получай анонимные сообщения"
    link = f"<code>t.me/anonymous_post_bot?start={message.from_user.id}</code>"
    await message.answer(template + "\n\n" + link, reply_markup=ReplyKeyboardRemove())


@form_router.message(CommandStart())
async def cmd_start_handler(
    message: Message, state: FSMContext, command: CommandObject
) -> None:
    match command.args:
        case None:
            await send_link(message, state)
        case str(message.from_user.id):
            await state.clear()
            await message.answer(
                f"⛔️ Извини, но ты не можешь отправить сообщение самому себе",
                reply_markup=ReplyKeyboardRemove(),
            )
        case _:
            await state.set_state(Form.user_to_user)
            await state.update_data(user_to_user=command.args)
            await message.answer(
                f"💬 Отправь своё анонимное послание\n(текст, голосовое, фото, видео или др.)",
                reply_markup=cancel_keyboard(),
            )


@form_router.callback_query(CallbackFactory.filter(F.action == Action.send_from_user))
async def cb_from_user_handler(
    callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
) -> None:
    await callback.answer()
    await state.set_state(Form.user_to_user)
    await state.update_data(user_to_user=callback_data.id)
    await callback.message.answer(
        "💬 Отправь своё анонимное послание\n(текст, голосовое, фото, видео или др.)",
        reply_markup=cancel_keyboard(),
    )


@form_router.callback_query(CallbackFactory.filter(F.action == Action.send_from_supp))
async def cb_from_support_handler(
    callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
) -> None:
    await callback.answer()
    await state.set_state(Form.support_to_user)
    await state.update_data(support_to_user=callback_data.id)
    await callback.message.answer(
        "⚠️ Сообщение будет отправлено от имени тех.поддержки",
        reply_markup=cancel_keyboard(),
    )


@form_router.message(Command("cancel"))
@form_router.message(F.text == "♻️ Отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("♻️ Отмена отправки", reply_markup=ReplyKeyboardRemove())


@form_router.message(Command("support"))
async def cmd_support_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.user_to_support)
    await message.answer(
        f"⚠️ Cледующее сообщение будет отправлено в чат технической пооддержки",
        reply_markup=cancel_keyboard(),
    )


def html_id_link(user: User) -> str:
    tg_link = f"tg://openmessage?user_id={user.id}"
    html_link = f"<a href='{tg_link}'>{user.full_name}</a>"
    return html_link


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

    new_msg_txt = "📨 Получено новое сообщение"
    if for_spt:
        new_msg_txt = "⚠️ Получено новое сообщение для тех.поддержки"
    if from_spt:
        new_msg_txt = "⚠️ Получено новое сообщение от тех.поддержки"
    if for_admin:
        new_msg_txt += f" от {html_id_link(message.from_user)}" if for_admin else ""
    new_msg_kb = profile_keyboard(from_whom_id) if for_admin else None
    await message.bot.send_message(to_whom_id, new_msg_txt, reply_markup=new_msg_kb)

    await message.copy_to(
        to_whom_id,
        reply_markup=answer_keyboard(from_whom_id, support=for_admin)
        if not from_spt
        else None,
    )

    await message.answer("✅ Cообщение отправлено!", reply_markup=ReplyKeyboardRemove())

    if not (for_spt or from_spt):
        await message.answer(
            "Хотите отправить еще одно сообщение этому пользователю?",
            reply_markup=answer_keyboard(to_whom_id, True),
        )


@form_router.message()
async def other_msg_handler(message: Message, state: FSMContext) -> None:
    await send_link(message, state)


@form_router.error(F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "⛔️ Упс, что-то пошло не так!",
        reply_markup=ReplyKeyboardRemove(),
    )


async def main():
    bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
