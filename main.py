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
                f"💬 Отправь своё анонимное послание для {'@' + chat.username if chat.username else chat.full_name} ответом на это сообщение",
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
                "✅ Cообщение отправлено!", reply_markup=ReplyKeyboardRemove()
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

# bot = Bot(token=config.TOKEN, parse_mode=types.ParseMode.HTML)
# dp = Dispatcher(bot)


# @dp.message_handler(
#     filters.ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=["start"]
# )
# async def bot_start(message: types.Message):
#     arg = message.get_args()
#     answer = f"🔗 Вот твоя личная ссылка, опубликуй её и получай анонимные сообщения\n\n<code>t.me/anonymous_post_bot?start={message.from_id}</code>"
#     if arg == str(message.from_id):
#         await message.answer(answer)
#         answer = "⛔️ Извини, но ты не можешь отправить сообщение самому себе"
#     elif len(arg) > 0:
#         try:
#             user = await bot.get_chat(arg)
#             answer = f"👤 {user.mention} [{arg}]\n\n💬 Отправь своё анонимное послание ответом на это сообщение"
#         except exceptions.ChatNotFound:
#             answer = "⛔️ Извини, пользователь не найден"
#     await message.answer(answer)


# def encrypt(id: str, timestamp: float):
#     enc_id = ""
#     key_str = str(timestamp).replace(".", "")
#     for i in range(len(id)):
#         char_code = ord(id[i])
#         key_digit = int(key_str[i % len(key_str)])
#         encrypted_char = char_code ^ key_digit
#         enc_id += str(encrypted_char).zfill(3)
#     return enc_id


# def decrypt(enc_id: str, timestamp: float):
#     id = ""
#     key_str = str(timestamp).replace(".", "")
#     for i in range(0, len(enc_id), 3):
#         encrypted_digit = int(enc_id[i : i + 3])
#         key_digit = int(key_str[(i // 3) % len(key_str)])
#         decrypted_char = chr(encrypted_digit ^ key_digit)
#         id += decrypted_char
#     return id


# @dp.message_handler(commands=["1start"])
# async def bot_1start(message: types.Message):
#     timestamp = message.date.timestamp()
#     id = "6094454193"
#     hash_value = encrypt(id, timestamp)
#     print(hash_value)
#     print(decrypt(hash_value, timestamp))


# @dp.message_handler(content_types=types.ContentTypes.TEXT, is_reply=True)
# async def bot_reply(message: types.Message):
#     if not message.reply_to_message.from_user.is_bot:
#         return

#     match = re.search(r"\[(\d+)\]", message.reply_to_message.text)
#     id = match.group(1) if match else None

#     if not id:
#         return

#     try:
#         anon_msg = f"Для тебя сообщение:\n\n{message.text}"
#         if id == "6094454193":
#             anon_msg = f"Для тебя сообщение от:\
#             \nmention: {message.from_user.mention}\
#             \nfull_name: {message.from_user.full_name}\
#             \nid: {message.from_user.id}\
#             \n\n{message.text}"
#         await bot.send_message(chat_id=id, text=anon_msg)
#         await message.answer("✅ Сообщение доствлено")
#     except exceptions.ChatNotFound:
#         await message.answer("⛔️ Извини, сообщение не доствлено")


# if __name__ == "__main__":
#     executor.start_polling(dp, skip_updates=True)
