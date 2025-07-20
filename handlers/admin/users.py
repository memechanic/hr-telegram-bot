import logging
from dataclasses import asdict

from aiogram import F
from aiogram import Router, Bot
from aiogram.client import bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from keyboards.keyboard_builder import get_inline_keyboard
from locales.loader import t
from service.pincode import create_deep_link
from service.users import get_admin_tg_id, get_user_data, update_user_info

router = Router()

logger = logging.Logger(__name__)

class UserWork(StatesGroup):
    accepted = State()

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
async def accept_user(callback: CallbackQuery, state: FSMContext):
    logger.debug('accept_user')

    user_id = int(callback.data.split(":")[1])
    await update_user_info(user_id, status=t("service.status.accept"))
    await notify_user(callback.bot, user_id, t("service.status.accept"))

    await callback.answer(text=t("admin.users.accept_user"), show_alert=True)
    await callback.message.answer(text=t("admin.users.add_work_info"))
    await state.update_data(user_id=user_id)
    await state.set_state(UserWork.accepted)

@router.message(UserWork.accepted, F.text)
async def add_work_info(message: Message, state: FSMContext):
    logger.debug('add_work_info')
    info = message.text.split('.')

    if len(info) != 2:
        await message.answer(text=t("admin.users.error"))
        return
    else:
        department, position = map(str.strip, info)
        user_id = await state.get_value('user_id')
        result = await update_user_info(user_id, department=department, position=position)

        if not result:
            await message.answer(text=t("admin.users.error"))
            return

        await state.clear()
        await message.answer(text=t("admin.users.update_success"))


@router.callback_query(F.data.startswith("decline:"))
async def decline_user(callback: CallbackQuery):
    logger.debug('decline_user')

    user_id = int(callback.data.split(":")[1])
    await update_user_info(user_id, status=t("service.status.declined"))
    await callback.answer(text=t("admin.users.decline_user"), show_alert=True)
    await notify_user(callback.bot, user_id, t("service.status.declined"))

async def notify_user(bot: Bot, user_id: int, status: str):
    logger.debug('notify_user')
    text = t(f"admin.users.{status}_notification")
    await bot.send_message(
        user_id,
        text=text
    )

@router.message(Command("link"))
async def create_invite_link_cmd(message: Message, bot: Bot):
    logger.debug('create_invite_link_cmd')

    link, pincode = await create_deep_link(bot)
    if link:
        await message.answer(text=t('admin.users.link', link=link, pincode=pincode),
                             parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        await message.answer(t("admin.users.error"))