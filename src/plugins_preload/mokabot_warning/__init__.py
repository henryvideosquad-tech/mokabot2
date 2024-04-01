"""
mokabot 异常状态通知插件
在 bot 断线后，向管理员发送通知
或在 bot 连续若干次调用 API 失败时（视为风控），向管理员发送通知
"""

import asyncio
from typing import Optional, Any

import httpx
import nonebot
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, ActionFailed
from nonebot.log import logger

from .config import *

driver = get_driver()
send_failed_count = 0


@driver.on_bot_disconnect
async def dead_notification() -> None:
    """在 bot 断线后，通过 telegram 向管理员发送通知"""
    await telegram_bot_say(message := 'bot 已断开与 Lagrange.OneBot 的 websocket 连接')
    logger.critical(message)


@Bot.on_called_api
async def ban_notification(bot: Bot, exception: Optional[Exception], api: str, data: dict[str, Any], result: Any):
    """连续 send_failed_max 次发送消息失败时，向管理员发送通知"""
    global send_failed_count

    if isinstance(exception, ActionFailed) and exception.info.get('msg') != 'MSG_NOT_FOUND' and api != 'get_msg':
        send_failed_count += 1
        logger.error(f'请求 API {api} 失败，原因：{exception.info.get("wording")}')
    else:
        send_failed_count = 0

    if send_failed_count == send_failed_max:
        await telegram_bot_say(message := f'bot 已连续 {send_failed_count} 次调用 API 失败，请上号检查是否风控')
        logger.critical(message)


async def telegram_bot_say(message: str):
    """通过 Telegram Bot 将异常状态通知发送给管理员"""
    async with httpx.AsyncClient() as client:
        await client.get(
            f'https://api.telegram.org/bot{token}/sendMessage',
            params={'chat_id': chat_id, 'text': message}
        )
