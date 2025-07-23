from typing import Optional

from aiogram.filters.callback_data import CallbackData

class MediaTagList(CallbackData, prefix="mtl"):
    tag: str
    number: Optional[int] = 0
    action: Optional[str] = None
    id: Optional[int] = None

# Для будущего изменения в handlers.admin.users при обработке запросов
# from enum import Enum
# class RequestAction(str, Enum):
#     accept = "accept"
#     decline = "decline"
#
# class UserRequestAction(CallbackData, prefix="ura"):
#     action: RequestAction
#     user_id: int