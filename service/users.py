from db.requests.users import get_user

async def is_user(tg_id: int) -> bool:
    result = await get_user(tg_id)
    return bool(result)

async def is_admin(tg_id: int) -> bool:
    result = await get_user(tg_id)
    return result.is_admin