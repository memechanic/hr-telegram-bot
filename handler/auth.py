from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
from service.pincode import create_deep_link, is_pincode_right

router = Router()

class AuthState(StatesGroup):
    user_auth = State()
    authorized = State()

# авторизация через дип-линк
@router.message(CommandStart(deep_link=True))
async def start_link(message: Message, command: CommandObject, state: FSMContext):
    pincode_raw = command.args
    success = await is_pincode_right(pincode_raw, encoded=True)
    if success:
        await state.set_state(AuthState.authorized)
        await message.answer("Вы успешно авторизированны")
    else:
        await state.set_state(AuthState.user_auth)
        await message.answer("Пин-код использован либо его не существует, попробуйте ввести пин-код вручную:")

# авторизация посредством ввода пин-кода пользователем
@router.message(CommandStart(deep_link=False))
async def start(message: Message, state: FSMContext):
    await message.answer("Приветствую, я HR бот! Чтобы продолжить, введи пин-код:")
    await state.set_state(AuthState.user_auth)

@router.message(AuthState.user_auth, F.text)
async def user_auth(message: Message, state: FSMContext):
    pincode = message.text.strip()
    if pincode.isdigit():
        success = await is_pincode_right(pincode)
        if success:
            await state.set_state(AuthState.authorized)
            await message.answer("Вы успешно авторизированны")
        else:
            await state.set_state(AuthState.user_auth)
            await message.answer("Пин-код использован либо его не существует, попробуйте ввести пин-код заново:")
    else:
        await state.set_state(AuthState.user_auth)
        await message.answer("Это не пин-код, попробуй еще раз:")

@router.message(AuthState.authorized)
async def authorized(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать, я HR бот! Чтобы получить больше информации о компании нажмите 'Информация'\n" +
                         "Чтобы получить информацию о командах нажмите на Меню слева от поля ввода.")

@router.message(Command("link"))
async def create_invite_link(message: Message, bot: Bot):
    link, pincode = await create_deep_link(bot)
    if link:
        text = f"Сгенерированный пин-код: <code>{pincode}</code>\nCcылка для сотрудника:\n<a>{link}</a>"
        await message.answer(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        await message.answer("Что-то пошло не так, попробуйте еще раз")