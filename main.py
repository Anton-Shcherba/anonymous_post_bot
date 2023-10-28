import config
import asyncio
from aiogram import Bot, Dispatcher, F, Router, exceptions
from aiogram.enums import ParseMode, ContentType
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


form_router = Router()


class Form(StatesGroup):
    id = State()


def create_anon_msg_markup(btn_text: str, to_whom_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"answer_{to_whom_id}",
                )
            ]
        ]
    )


def create_сancel_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="♻️ Отмена")]],
        input_field_placeholder="Введите текст...",
        resize_keyboard=True,
    )


async def handle_exceptions(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "⛔️ Извини, пользователь не найден",
        reply_markup=ReplyKeyboardRemove(),
    )


async def start_anonymous_msg_workflow(
    to_whom_id: str, message: Message, state: FSMContext
) -> None:
    await state.set_state(Form.id)
    await state.update_data(id=to_whom_id)
    await message.answer(
        f"💬 Отправь своё анонимное послание\n(<i>текст, голосовое, фото, видео или др.</i>)",
        reply_markup=create_сancel_markup(),
    )


async def send_link(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        f"🔗 Вот твоя личная ссылка, опубликуй её и получай анонимные сообщения\n\n<code>t.me/anonymous_post_bot?start={message.from_user.id}</code>",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.callback_query()
async def callback_query_handler(
    callback_query: CallbackQuery, state: FSMContext
) -> None:
    if callback_query.data and callback_query.data.startswith("answer_"):
        try:
            to_whom_id = callback_query.data[7:]
            await callback_query.answer()
            await callback_query.bot.get_chat(to_whom_id)
            await start_anonymous_msg_workflow(
                to_whom_id, callback_query.message, state
            )
        except exceptions.TelegramBadRequest:
            await handle_exceptions(callback_query.message, state)


@form_router.message(CommandStart())
async def command_start_handler(
    message: Message, state: FSMContext, command: CommandObject
) -> None:
    if not command.args:
        await send_link(message, state)
    elif command.args == str(message.from_user.id):
        await state.clear()
        await message.answer(
            f"⛔️ Извини, но ты не можешь отправить сообщение самому себе",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        try:
            await message.bot.get_chat(command.args)
            await start_anonymous_msg_workflow(command.args, message, state)
        except exceptions.TelegramBadRequest:
            await handle_exceptions(message, state)


@form_router.message(Command("cancel"))
@form_router.message(F.text == "♻️ Отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "♻️ Отмена отправки",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("support"))
async def start_support_msg_workflow(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.id)
    await state.update_data(id="support")
    await message.answer(
        f"⚠️ Cледующее сообщение будет отправлено в чат технической пооддержки",
        reply_markup=create_сancel_markup(),
    )


@form_router.message(Form.id)
async def process_state_id(message: Message, state: FSMContext) -> None:
    current_state = await state.get_data()
    to_whom_id: str | None = current_state.get("id")
    await state.clear()
    if not to_whom_id:
        await message.answer("⛔️ Ошибка", reply_markup=ReplyKeyboardRemove())
    else:
        is_support = to_whom_id == "support"
        to_whom_id = config.ADMIN_ID if is_support else to_whom_id
        is_admin = to_whom_id == config.ADMIN_ID
        try:
            await message.bot.send_message(
                to_whom_id,
                f"📨 <b>Получено новое сообщение{' для технической пооддержки' if is_support else ''}</b>"
                + f"\n\n<b>имя</b>: {message.from_user.mention_html()}\n<b>юзернэйм</b>: @{message.from_user.username}\n<b>id</b>: {message.from_user.id}"
                if is_admin
                else "",
            )
            await message.copy_to(
                to_whom_id,
                reply_markup=create_anon_msg_markup(
                    f"{'⚠️' if is_support else '🔄'} Ответить", message.from_user.id
                ),
            )
            await message.answer(
                f"✅ Cообщение отправлено{' в чат технической пооддержки' if is_support else ''}!",
                reply_markup=ReplyKeyboardRemove(),
            )
            if not is_support:
                await message.answer(
                    "<i>Хотите отправить еще одно сообщение этому пользователю?</i>",
                    reply_markup=create_anon_msg_markup("🔄 Отправить ещё", to_whom_id),
                )
        except exceptions.TelegramBadRequest:
            await handle_exceptions(message, state)


@form_router.message()
async def other_msg_handler(message: Message, state: FSMContext) -> None:
    await send_link(message, state)


async def main():
    bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
