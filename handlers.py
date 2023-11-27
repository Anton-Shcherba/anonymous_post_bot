import config, text
from keyboards import cancel_kb, profile_kb, answer_kb
from states import Action, CallbackFactory, Form
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    CallbackQuery,
    ErrorEvent,
)


router = Router()


async def send_link(message: Message, state: FSMContext) -> None:
    await state.clear()
    bot_name = (await message.bot.get_me()).username
    start_link_msg = text.start_msg_tmpl.format(id=message.from_user.id, bot=bot_name)
    await message.answer(start_link_msg, reply_markup=ReplyKeyboardRemove())


@router.message(CommandStart())
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
            await message.answer(text.send_msg, reply_markup=cancel_kb)


@router.callback_query(CallbackFactory.filter(F.action == Action.send_from_user))
async def cb_from_user_handler(
    callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
) -> None:
    await callback.answer()
    await state.set_state(Form.user_to_user)
    await state.update_data(user_to_user=callback_data.id)
    await callback.message.answer(text.send_msg, reply_markup=cancel_kb)


@router.callback_query(CallbackFactory.filter(F.action == Action.send_from_supp))
async def cb_from_support_handler(
    callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext
) -> None:
    await callback.answer()
    await state.set_state(Form.support_to_user)
    await state.update_data(support_to_user=callback_data.id)
    await callback.message.answer(text.send_from_supp, reply_markup=cancel_kb)


@router.message(Command("cancel"))
@router.message(F.text == text.cancel)
async def cmd_cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text.cancel_msg, reply_markup=ReplyKeyboardRemove())


@router.message(Command("support"))
async def cmd_support_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.user_to_support)
    await message.answer(text.send_to_supp, reply_markup=cancel_kb)


async def state_parse(state: FSMContext) -> tuple[str, bool, bool, bool]:
    current_state = await state.get_state()
    data = await state.get_data()
    match current_state:
        case Form.user_to_user:
            id = data.get(Form.user_to_user._state)
            return (id, id == config.ADMIN_ID, False, False)
        case Form.user_to_support:
            return (config.ADMIN_ID, True, True, False)
        case Form.support_to_user:
            return (data.get(Form.support_to_user._state), False, False, True)


@router.message(~StateFilter(None))
async def state_handler(message: Message, state: FSMContext) -> None:
    to_whom_id, for_admin, for_spt, from_spt = await state_parse(state)
    from_whom_id = message.from_user.id
    await state.clear()

    msg_txt = text.msg_recv_spt if for_spt or from_spt else text.msg_recv
    msg_txt += text.id_link_tmpl.format(id=message.from_user.id) if for_admin else ""
    new_msg_kb = profile_kb(from_whom_id) if for_admin else None
    await message.bot.send_message(to_whom_id, msg_txt, reply_markup=new_msg_kb)

    copy_msg_kb = None if from_spt else answer_kb(from_whom_id, supp=for_admin)

    await message.copy_to(to_whom_id, reply_markup=copy_msg_kb)

    await message.answer(text.msg_sent, reply_markup=ReplyKeyboardRemove())

    if not (for_spt or from_spt):
        one_more_kb = answer_kb(to_whom_id, True)
        await message.answer(text.one_more_msg, reply_markup=one_more_kb)


@router.message()
async def other_msg_handler(message: Message, state: FSMContext) -> None:
    await send_link(message, state)


@router.error(F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text.any_err, reply_markup=ReplyKeyboardRemove())
