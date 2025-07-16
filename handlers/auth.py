from aiogram import F
from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from locales.loader import t
from service.pincode import is_pincode_right

router = Router()

class UserAuth(StatesGroup):
    pincode = State()
    first_name = State()
    last_name = State()
    phone_number = State()
    email = State()
    confirm = State()

# авторизация через дип-линк
@router.message(CommandStart(deep_link=True))
async def start_link(message: Message, command: CommandObject, state: FSMContext):
    pincode_raw = command.args
    success = await is_pincode_right(pincode_raw, encoded=True)
    if success:
        await state.set_state(UserAuth.first_name)
        await message.answer(text=t('auth.success'))
    else:
        await state.set_state(UserAuth.pincode)
        await message.answer(text=t('auth.link_error'))

# авторизация посредством ввода пин-кода пользователем
@router.message(CommandStart(deep_link=False))
async def start_cmd(message: Message, state: FSMContext):
    await message.answer(text=t('auth.start'))
    await state.set_state(UserAuth.pincode)

@router.message(UserAuth.pincode, F.text)
async def user_auth(message: Message, state: FSMContext):
    pincode = message.text.strip()
    if pincode.isdigit():
        success = await is_pincode_right(pincode)
        if success:
            await state.set_state(UserAuth.first_name)
            await message.answer(text=t('auth.success'))
        else:
            await state.set_state(UserAuth.pincode)
            await message.answer(text=t('auth.pincode_error'))
    else:
        await state.set_state(UserAuth.pincode)
        await message.answer(text=t('auth.pincode_error'))

# Прежде чем начать введите свои данные
# Ввод имя, фамилия, номер телефона, почта -> проверьте данные 1. Отправить на подтверждение 2. Изменить данные

@router.message(UserAuth.first_name, F.text)
async def get_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(UserAuth.last_name)
    await message.answer(text=t('auth.first_name'))

@router.message(UserAuth.last_name, F.text)
async def get_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(UserAuth.phone_number)
    await message.answer(text=t('auth.last_name'))

@router.message(UserAuth.phone_number, F.text)
async def get_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await state.set_state(UserAuth.email)
    await message.answer(text=t('auth.phone_number'))

@router.message(UserAuth.email, F.text)
async def get_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(UserAuth.confirm)
    await message.answer(text=t('auth.email'))

"""
# ### План
# Добавить проверку данных 
# Добавить сборку данных и загрузку их в бд
# Добавить клавиатуру для подтверждения и отправки
# Придумать как изменить данные по одному, либо сделать все заново

@router.message(UserAuth.confirm, F.text.contains("Отправить"))
async def confirm_data(message: Message, state: FSMContext):
    await state.update_data()

@router.message(UserAuth.confirm, F.text.contains("Изменить"))
async def change_data(message: Message, state: FSMContext):
    await state.update_data()
"""