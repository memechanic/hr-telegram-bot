import logging

from aiogram import F, Bot
from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, BotCommandScopeChat

from handlers.admin.users import add_user_request
from keyboards.keyboard_builder import get_inline_keyboard, get_reply_keyboard
from locales.loader import t
from service.pincode import is_pincode_right
from service.users import add_pending_user, is_user, is_admin
from service.validators import is_text, is_phone_number, is_email
from app.commands import COMMANDS, USER_COMMANDS, ADMIN_COMMANDS

router = Router()

logger = logging.getLogger(__name__)

class UserAuth(StatesGroup):
    pincode = State()
    full_name = State()
    phone_number = State()
    email = State()
    confirm = State()
    change = State()

# авторизация через дип-линк
@router.message(CommandStart(deep_link=True))
async def start_link(message: Message, bot: Bot, command: CommandObject, state: FSMContext):
    logger.debug('start_link')

    user_id = message.from_user.id
    await bot.set_my_commands(COMMANDS, BotCommandScopeChat(chat_id=user_id))

    pincode_raw = command.args
    success = await is_pincode_right(pincode_raw, encoded=True)
    if success:
        await state.set_state(UserAuth.full_name)
        await message.answer(text=t('auth.pin_success'))
    else:
        await state.set_state(UserAuth.pincode)
        await message.answer(text=t('auth.link_error'))

# авторизация посредством ввода пин-кода пользователем
@router.message(CommandStart(deep_link=False))
async def start_cmd(message: Message, bot: Bot, state: FSMContext):
    logger.debug('start_cmd')
    user_id = message.from_user.id

    if not await is_user(user_id):
        await bot.set_my_commands(COMMANDS, BotCommandScopeChat(chat_id=user_id))
        await message.answer(text=t('auth.start'))
        await state.set_state(UserAuth.pincode)

    else: await authorized_user(message, bot)

async def authorized_user(message: Message, bot: Bot):
    user_id = message.from_user.id

    if await is_user(user_id) and not await is_admin(user_id):
        await bot.set_my_commands(USER_COMMANDS, BotCommandScopeChat(chat_id=user_id))

    elif await is_admin(user_id):
        await bot.set_my_commands(ADMIN_COMMANDS, BotCommandScopeChat(chat_id=user_id))

    await message.answer(text=t('support.help'))

@router.message(UserAuth.pincode, F.text)
async def user_auth(message: Message, state: FSMContext):
    logger.debug('user_auth')

    pincode = message.text.strip()
    success = await is_pincode_right(pincode)
    if success:
        await state.set_state(UserAuth.full_name)
        await message.answer(text=t('auth.pin_success'))
    else:
        await message.answer(text=t('auth.pincode_error'))

# Получение данных о пользователе
@router.message(UserAuth.full_name, F.text)
async def get_full_name(message: Message, state: FSMContext):
    logger.debug('get_full_name')

    first_name, last_name, patronym = ("-", "-", "-")
    full_name = [p.strip() for p in message.text.strip().split()]

    if not (len(full_name) in (2, 3) and all(is_text(p) for p in full_name)):
        await message.answer(text=t('auth.validation_error'))
        return

    if len(full_name) == 2:
        first_name, last_name = full_name
    else:
        first_name, last_name, patronym = map(str.strip, full_name)

    await state.update_data(first_name=first_name, last_name=last_name, patronym=patronym)
    await state.set_state(UserAuth.phone_number)
    await message.answer(text=t('auth.full_name'))

@router.message(UserAuth.phone_number, F.text)
async def get_phone_number(message: Message, state: FSMContext):
    logger.debug('get_phone_number')

    phone_number = message.text.strip()
    if is_phone_number(phone_number):
        await state.update_data(phone_number=phone_number)
        await state.set_state(UserAuth.email)
        await message.answer(text=t('auth.phone_number'))
    else:
        await message.answer(text=t('auth.validation_error'))

@router.message(UserAuth.email, F.text)
async def get_email(message: Message, state: FSMContext):
    logger.debug('get_email')

    email = message.text.strip()
    if not is_email(email):
        await message.answer(text=t('auth.validation_error'))
        return
    await state.update_data(email=email)
    await get_confirm(message, state)

# Подтверждение данных
async def get_confirm(message: Message, state: FSMContext):
    logger.debug('get_confirm')

    await state.set_state(UserAuth.confirm)
    data = await state.get_data()
    buttons = {
        'confirm': t('auth.buttons.confirm'),
        'change': t('auth.buttons.change'),
    }
    await message.answer(
        text=t('auth.confirm', **data),
        reply_markup=get_inline_keyboard(buttons)
    )

@router.callback_query(UserAuth.confirm, F.data == "confirm")
async def confirm(callback: CallbackQuery, state: FSMContext):
    logger.debug('confirm')

    data = await state.get_data()
    data['tg_id'] = callback.from_user.id
    data['tg_username'] = callback.from_user.username

    result = await add_pending_user(data)
    if not result:
        await callback.message.answer(text=t('auth.add_user_error'))
        await callback.answer()
        return

    await add_user_request(callback.bot, data['tg_id'])
    await state.clear()
    await callback.message.answer(text=t('auth.auth_confirmed'))
    await callback.answer()

@router.callback_query(UserAuth.confirm, F.data == "change")
async def change(callback: CallbackQuery, state: FSMContext):
    logger.debug('change')

    buttons = [
        t('auth.buttons.full_name'),
        t('auth.buttons.email'),
        t('auth.buttons.phone_number')
    ]
    keyboard = get_reply_keyboard(buttons)
    await state.set_state(UserAuth.change)
    await callback.message.answer(t('auth.change'), reply_markup=keyboard)
    await callback.answer()

@router.message(UserAuth.change, F.text)
async def change(message: Message, state: FSMContext):

    pass

"""
# ### План
# Придумать как изменить данные по одному, либо сделать все заново

"""