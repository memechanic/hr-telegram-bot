import asyncio
import logging

from aiogram import F, Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_reader import config

from app.commands import COMMANDS

bot = Bot(token=config.bot_token.get_secret_value())

dp = Dispatcher()

@dp.startup()
async def on_startup(bot: Bot):
    await bot.set_my_commands(COMMANDS)


@dp.message(F.text, Command("start"))
async def cmd_start_handler(message: types.Message):
    await message.answer(f"Hello, {message.from_user.full_name}!")

@dp.message(Command("dice"))
async def cmd_dice_handler(message: types.Message):
    await message.answer_dice(emoji="🎲")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutdown requested")