import asyncio
import logging

from aiogram import Bot, Dispatcher, Router

from app.commands import COMMANDS
from config_reader import config
from handlers import auth, support, info, modular_info
from handlers.admin import users, content
from locales.loader import reload_locale
from middlewares import CheckUserMiddleware

dp = Dispatcher()

@dp.startup()
async def on_startup(bot: Bot):
    reload_locale()
    await bot.set_my_commands(COMMANDS)

async def main():
    bot = Bot(token=config.bot_token.get_secret_value())

    # Роутеры для не авторизированных пользователей
    auth_router = Router()
    auth_router.include_router(auth.router)

    # Роутеры для авторизированных пользователей
    users_router = Router()
    users_router.include_router(support.router)
    users_router.include_router(info.router)
    users_router.include_router(modular_info.router)

    users_router.message.middleware(CheckUserMiddleware("user"))

    # Роутеры для администрации
    admin_router = Router()
    admin_router.include_router(users.router)
    admin_router.include_router(content.router)

    admin_router.message.middleware(CheckUserMiddleware("admin"))

    #Сбор всех роутеров
    dp.include_router(users_router)
    dp.include_router(admin_router)
    dp.include_router(auth_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s::%(levelname)s::%(name)s::%(message)s')

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown requested")