from random import randint

from aiogram import Bot
from aiogram.utils.deep_linking import create_start_link, decode_payload

from db.requests import add_pincode, get_pincode, update_used_pincode

MIN_PINCODE = 1000
MAX_PINCODE = 9999

async def create_pincode(attempts: int = 10) -> int | None:
    while attempts > 0:
        pincode = randint(MIN_PINCODE, MAX_PINCODE)
        inserted = await add_pincode(pincode)
        if inserted:
            return pincode
        attempts -= 1
    return None

async def create_deep_link(bot: Bot) -> (str, int):
    pincode = await create_pincode()
    if pincode:
        link = await create_start_link(bot, str(pincode), encode=True)
        return link, pincode
    else:
        return None, None

async def is_pincode_right(payload: str) -> bool:
    pincode = int(decode_payload(payload))
    result = await get_pincode(pincode)

    if result and not result.is_used:
        await update_used_pincode(pincode)
        return True
    else: return False