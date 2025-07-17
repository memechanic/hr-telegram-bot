import asyncio
import logging

from aiogram import Bot, Dispatcher, Router

from app.commands import COMMANDS
from config_reader import config
from handlers import auth, support
from handlers.admin import users
from middlewares import AuthMiddleware, AdminMiddleware
from locales.loader import reload_locale

dp = Dispatcher()

@dp.startup()
async def on_startup(bot: Bot):
    reload_locale()
    await bot.set_my_commands(COMMANDS)

async def main():
    bot = Bot(token=config.bot_token.get_secret_value())

    # Роутеры для не авторизированных пользователей
    dp.include_router(auth.router)

    # Роутеры для авторизированных пользователей
    users_router = Router()
    users_router.include_router(support.router)

    users_router.message.middleware(AuthMiddleware())

    # Роутеры для администрации
    admin_router = Router()
    admin_router.include_router(users.router)

    admin_router.message.middleware(AdminMiddleware())

    #Сбор всех роутеров
    dp.include_router(users_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutdown requested")