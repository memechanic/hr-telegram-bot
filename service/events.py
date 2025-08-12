import logging
from datetime import datetime
from typing import List, Dict

from db.requests.events import add_event, get_events, delete_event
from db.models import Event, EventTypeEnum

logger = logging.getLogger(__name__)

EVENTS_TYPE_LABELS = {
    "Корпоративное мероприятие": EventTypeEnum.event.value,
    "Экскурсия": EventTypeEnum.excursion.value,
}

EVENTS_TYPES = {
    EventTypeEnum.event.value: "Корпоративное мероприятие",
    EventTypeEnum.excursion.value: "Экскурсия",
}

async def validate_datetime(string_time: str) -> datetime | None:
    logger.debug(f"validate_datetime")

    try:
        dt = datetime.strptime(string_time, "%d.%m.%Y %H:%M")
    except ValueError:
        return None
    else:
        return dt

async def get_all_events() -> List[Dict]:
    logger.debug(f"get_all_events")
    events = []
    result = await get_events(True)
    for e in result:
        event_data = {
            "id": e.id,
            "event_type": e.type,
            "title": e.title,
            "description": e.description,
            "address": e.address,
            "start_time": e.start_time,
            "end_time": e.end_time,
        }
        events.append(event_data)
    return events

async def get_corp_events() -> List[Dict]:
    logger.debug(f"get_corp_events")
    events = []
    w = Event.type == EventTypeEnum.event
    result = await get_events(w)
    for e in result:
        event_data = {
            "id": e.id,
            "event_type": e.type,
            "title": e.title,
            "description": e.description,
            "address": e.address,
            "start_time": e.start_time,
            "end_time": e.end_time,
        }
        events.append(event_data)
    return events

async def add_corp_event(event_data: Dict) -> bool:
    logger.debug(f"add_corp_event")

    event = Event(
        type=event_data["event_type"],
        title=event_data["title"],
        description=event_data["description"],
        address=event_data["address"],
        start_time=event_data["start_time"],
        end_time=event_data["end_time"],
    )

    result = await add_event(event)
    return result

async def delete_event_by_id(event_id: int) -> bool:
    logger.debug(f"delete_event_by_id")

    stmt = Event.id == event_id
    result = await delete_event(stmt)
    return bool(result)