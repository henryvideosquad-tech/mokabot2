from collections import deque
from time import time
from typing import Optional, Any

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent
from nonebot.message import event_preprocessor

from src.utils.mokabot_humanize import SecondHumanizeUtils, format_timestamp

driver = get_driver()

MOKABOT_START_TIME = time()
last_message_time = 0
count_message_sent = 0
count_message_received = 0
count_disconnect_times = 0


class TimeIntervalCounter:
    def __init__(self):
        self.timestamps = deque()

    def add_timestamp(self):
        self.timestamps.append(time())
        # Perform cleanup every 1000 timestamps
        if len(self.timestamps) % 1000 == 0:
            self._cleanup()

    def count_last_minute(self):
        return self._count_last_seconds(60)

    def count_last_hour(self):
        return self._count_last_seconds(60 * 60)

    def count_last_day(self):
        return self._count_last_seconds(60 * 60 * 24)

    def _count_last_seconds(self, seconds):
        cutoff = time() - seconds
        return sum(1 for ts in self.timestamps if ts >= cutoff)

    def _cleanup(self):
        cutoff = time() - 60 * 60 * 24  # One day ago
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()


message_counter = TimeIntervalCounter()


def get_bot_uptime() -> str:
    uptime = time() - MOKABOT_START_TIME
    return SecondHumanizeUtils(uptime).to_datetime()


def get_last_message_time() -> str:
    return format_timestamp('%Y-%m-%d %H:%M:%S', last_message_time)


def get_message_sent_count() -> int:
    return count_message_sent


def get_message_received_count() -> int:
    return count_message_received


def get_disconnect_times() -> int:
    return count_disconnect_times


@Bot.on_called_api
async def _(bot: Bot, exception: Optional[Exception], api: str, data: dict[str, Any], result: Any):
    global count_message_sent, last_message_time
    if api in ['send_msg', 'send_private_msg', 'send_group_msg', 'send_group_forward_msg']:
        count_message_sent += 1
        message_counter.add_timestamp()
        last_message_time = time()


@event_preprocessor
async def _(event: Event):
    global count_message_received
    if isinstance(event, MessageEvent) and event.sender.user_id != event.self_id:
        count_message_received += 1
        message_counter.add_timestamp()


@driver.on_bot_disconnect
async def _():
    global count_disconnect_times
    count_disconnect_times += 1
