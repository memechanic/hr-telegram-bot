import logging

from db.requests.users import get_user, add_user, get_admin, update_user, delete_user
from db.models import User
from locales.loader import t

logger = logging.Logger(__name__)

async def is_user(tg_id: int) -> bool:
    logger.debug('is_user')

    result = await get_user(tg_id)
    if result:
        return result.status != t('service.status.declined')
    else: return False

async def is_admin(tg_id: int) -> bool:
    logger.debug('is_admin')

    result = await get_user(tg_id)
    return bool(result and result.is_admin)

async def get_admin_tg_id() -> int:
    logger.debug('get_admin_tg_id')

    admin = await get_admin()
    return admin.tg_id

async def add_pending_user(data: dict) -> bool:
    logger.debug('add_pending_user')

    user = User(
        tg_id=data['tg_id'],
        tg_username=data['tg_username'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        patronym=data['patronym'],
        phone_number=data['phone_number'],
        email=data['email'],
        status=t('service.status.pending'),
    )
    result = await add_user(user)
    return result

async def delete_declined_user(tg_id: int) -> bool:
    logger.debug('delete_user')
    return await delete_user(tg_id, 'status', t("service.status.declined"))

async def update_user_info(user_id: int, **kwargs) -> bool:
    logger.debug('update_user_info')
    return await update_user(user_id, **kwargs)

async def get_user_data(tg_id: int) -> dict | None:
    logger.debug('get_user_data')

    user = await get_user(tg_id)
    if not user:
        return None
    data = {
        "id": user.id,
        "tg_id": user.tg_id,
        "tg_username": user.tg_username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "patronym": user.patronym,
        "phone_number": user.phone_number,
        "email": user.email,
        "status": user.status,
    }
    return data