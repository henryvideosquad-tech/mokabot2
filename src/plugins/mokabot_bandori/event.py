from io import BytesIO
from time import time

from pytz import timezone

from src.utils.mokabot_text2image import to_bytes_io
from .bestdori import get_events_all
from .bestdori.model import Language

CACHE_TIMESTAMP = 0


async def generate_event_list(region: Language) -> BytesIO:
    if time() - CACHE_TIMESTAMP > 60 * 60 * 24:
        events_all = await get_events_all()
    else:
        events_all = await get_events_all(is_cache=True)
    beijing_tz = timezone('Asia/Shanghai')
    text = '活动列表：\n'

    for index, event in reversed(events_all.__root__.items()):
        if event.startAt[region] is None or event.endAt[region] is None:
            continue

        start = event.startAt[region].replace(tzinfo=beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        end = event.endAt[region].replace(tzinfo=beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
        text += f'{start}~{end}\n'
        text += f'{index:<5} {event.eventName[region]}\n'

    return to_bytes_io(text)
