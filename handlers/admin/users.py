from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode

from service.pincode import create_deep_link
from locales.loader import t

router = Router()

"""
/add_user
/remove_user
/edit_user

/link - для получения ссылки для нового пользователя

одобрение заявок пользователей
"""

@router.message(Command("link"))
async def create_invite_link_cmd(message: Message, bot: Bot):
    link, pincode = await create_deep_link(bot)
    if link:
        await message.answer(text=t('admin.users.link', link=link, pincode=pincode),
                             parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        await message.answer(t("admin.users.link_error"))