import logging

from aiogram import F
from aiogram import Router, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards.keyboard_builder import get_inline_keyboard
from locales.loader import t
from service.pincode import create_deep_link
from service.users import get_admin_tg_id, get_user_data, update_user_status

router = Router()

logger = logging.Logger(__name__)

"""
/add_user
/remove_user
/edit_user

"""


async def add_user_request(bot: Bot, user_id: int):
    logger.debug('add_user_request')

    admin_tg_id = await get_admin_tg_id()
    user = await get_user_data(user_id)

    buttons = {
        "accept:" + str(user_id): t('admin.users.buttons.accept'),
        "decline:" + str(user_id): t('admin.users.buttons.decline'),
    }
    keyboard = get_inline_keyboard(buttons)
    await bot.send_message(
        admin_tg_id,
        text=t("admin.users.add_user_request", **user),
        reply_markup=keyboard,
    )

@router.callback_query(F.data.startswith("accept:"))
async def accept_user(callback: CallbackQuery):
    logger.debug('accept_user')

    user_id = int(callback.data.split(":")[1])
    await update_user_status(user_id, t("service.status.accept"))
    await callback.answer(text=t("admin.users.accept_user"), show_alert=True)

@router.callback_query(F.data.startswith("decline:"))
async def decline_user(callback: CallbackQuery):
    logger.debug('decline_user')

    user_id = int(callback.data.split(":")[1])
    await update_user_status(user_id, t("service.status.declined"))
    await callback.answer(text=t("admin.users.decline_user"), show_alert=True)

@router.message(Command("link"))
async def create_invite_link_cmd(message: Message, bot: Bot):
    logger.debug('create_invite_link_cmd')

    link, pincode = await create_deep_link(bot)
    if link:
        await message.answer(text=t('admin.users.link', link=link, pincode=pincode),
                             parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        await message.answer(t("admin.users.error"))