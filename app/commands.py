from aiogram.types import BotCommand
from locales.loader import t
COMMANDS = [
    BotCommand(command="start", description=t("service.commands.start")),
]

USER_COMMANDS = COMMANDS + [
    BotCommand(command="help", description=t("service.commands.help")),
    BotCommand(command="company", description=t("service.commands.company")),
    BotCommand(command="cafeteria", description=t("service.commands.cafeteria")),
]

ADMIN_COMMANDS = USER_COMMANDS + [
    BotCommand(command="link", description=t("service.commands.link")),
    BotCommand(command="content", description=t("service.commands.content")),
]