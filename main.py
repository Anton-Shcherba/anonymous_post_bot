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
    CallbackQuery,
)
import re
import hashlib

form_router = Router()


class Form(StatesGroup):
    id = State()


# TODO
# ситуация со стэйтом отправки и получением сообщения
# обработка всех типов сообщений
# обработка собщений при нулевом состоянии


@form_router.callback_query()
async def callback_query_handler(
    callback_query: CallbackQuery, state: FSMContext
) -> Any:
    if callback_query.data:
        data_list = callback_query.data.split("_")
        if len(data_list) == 2 and data_list[0] == "answer":
            try:
                await callback_query.bot.get_chat(data_list[1])
                await state.set_state(Form.id)
                await state.update_data(id=data_list[1])
                await callback_query.message.answer(
                    f"💬 Отправь своё анонимное послание",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton(text="⛔️ Отмена")]],
                        input_field_placeholder="Введите текст...",
                        resize_keyboard=True,
                    ),
                )
                await callback_query.answer()
            except exceptions.TelegramBadRequest:
                await state.clear()
                await callback_query.message.answer(
                    "⛔️ Извини, пользователь не найден",
                    reply_markup=ReplyKeyboardRemove(),
                )


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
            await message.bot.get_chat(command.args)
            await state.set_state(Form.id)
            await state.update_data(id=command.args)
            await message.answer(
                f"💬 Отправь своё анонимное послание",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="⛔️ Отмена")]],
                    input_field_placeholder="Введите текст...",
                    resize_keyboard=True,
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
                id,
                f"📨 <b>Получено новое сообщение</b>\n\n{message.text}",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🔄 Ответить",
                                callback_data=f"answer_{message.from_user.id}",
                            )
                        ]
                    ]
                ),
            )
            await message.answer(
                "✅ Cообщение отправлено!",
                reply_markup=ReplyKeyboardRemove(),
            )
            await message.answer(
                "<i>Хотите отправить еще одно сообщение этому пользователю?</i>",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🔄 Отправить ещё",
                                callback_data=f"answer_{id}",
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
