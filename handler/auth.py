from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode

from service.pincode import create_deep_link, is_pincode_right

router = Router()

# авторизация через дип-линк
@router.message(CommandStart(deep_link=True))
async def start_pincode(message: Message, command: CommandObject):
    pincode_raw = command.args
    success = await is_pincode_right(pincode_raw)
    if success:
        await message.answer("Успешно авторизирован")
    else:
        await message.answer("Пин-код использован либо его не существует")

# авторизация посредством ввода пин-кода пользователем
@router.message(CommandStart())
async def start(message: Message):
    pass

@router.message(Command("link"))
async def create_invite_link(message: Message, bot: Bot):
    link, pincode = await create_deep_link(bot)
    if link:
        text = f"Сгенерированный пин-код: <code>{pincode}</code>\nCcылка для сотрудника:\n<a>{link}</a>"
        await message.answer(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        await message.answer("Что-то пошло не так, попробуйте еще раз")