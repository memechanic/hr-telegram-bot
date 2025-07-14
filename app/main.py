import asyncio
import logging

from aiogram import F, Bot, Dispatcher
from config_reader import config

from app.commands import COMMANDS
from handler import auth

dp = Dispatcher()

@dp.startup()
async def on_startup(bot: Bot):
    await bot.set_my_commands(COMMANDS)

async def main():
    bot = Bot(token=config.bot_token.get_secret_value())

    dp.include_router(auth.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutdown requested")