import config
from aiogram import F, Router
from aiogram.types import (
    Message,
    InlineQuery,
    InlineQueryResultVoice,
)
from data import voice_dict

router = Router()


@router.message(F.voice & F.from_user.id == int(config.ADMIN_ID))
async def other_msg_handler(message: Message) -> None:
    await message.answer(message.voice.file_id)


results_list = [
    InlineQueryResultVoice(id=str(i), voice_url=x[0], title=x[1])
    for i, x in enumerate(voice_dict.items())
]


@router.inline_query()
async def inline_query_handler(query: InlineQuery):
    search_query = query.query.replace("ё", "е").lower()
    results = [x for x in results_list if search_query in x.title]
    await query.answer(results)
