import config
import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict

from aiogram import Bot, Dispatcher, F, Router, html, exceptions
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import re
import hashlib

form_router = Router()


class Form(StatesGroup):
    id = State()


@form_router.message(CommandStart())
async def command_start(
    message: Message, state: FSMContext, command: CommandObject
) -> None:
    if not command.args:
        await state.clear()
        await message.answer(
            f"🔗 Вот твоя личная ссылка, опубликуй её и получай анонимные сообщения\n\n<code>t.me/anonymous_post_bot?start={message.from_user.id}</code>",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif command.args == str(message.from_user.id):
        await state.clear()
        await message.answer(
            f"⛔️ Извини, но ты не можешь отправить сообщение самому себе",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        try:
            chat = await message.bot.get_chat(command.args)
            await state.set_state(Form.id)
            await state.update_data(id=command.args)
            await message.answer(
                f"💬 Отправь своё анонимное послание для {'@' + chat.username if chat.username else chat.full_name}",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="⛔️ Отмена")]], resize_keyboard=True
                ),
            )
        except exceptions.TelegramBadRequest:
            await state.clear()
            await message.answer(
                "⛔️ Извини, пользователь не найден", reply_markup=ReplyKeyboardRemove()
            )


@form_router.message(Command("cancel"))
@form_router.message(F.text == "⛔️ Отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "⛔️ Отмена отправки",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.id)
async def process_id(message: Message, state: FSMContext) -> None:
    current_state = await state.get_data()
    id = current_state.get("id")
    await state.clear()
    if not id:
        await message.answer("⛔️ Ошибка", reply_markup=ReplyKeyboardRemove())
    else:
        try:
            await message.bot.send_message(
                id, f"📨 <b>Получено новое сообщение</b>\n\n{message.text}"
            )
            await message.answer(
                "✅ Cообщение отправлено!",
                reply_markup=ReplyKeyboardRemove(),
            )
            await message.answer(
                "<i>Хотите отправить еще одно сообщение?</i>",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🔄 Отправить ещё",
                                url=f"t.me/anonymous_post_bot?start={id}",
                            )
                        ]
                    ]
                ),
            )
        except exceptions.TelegramBadRequest:
            await state.clear()
            await message.answer(
                "⛔️ Извини, пользователь не найден", reply_markup=ReplyKeyboardRemove()
            )


async def main():
    bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
