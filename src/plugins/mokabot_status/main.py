from textwrap import dedent

from nonebot import on_command, on_type
from nonebot.adapters.onebot.v11 import Bot, PokeNotifyEvent
from nonebot.rule import to_me

from .mokabot import (
    get_bot_uptime, message_counter,
    get_last_message_time, get_message_sent_count, get_message_received_count, get_disconnect_times
)
from .onebot import get_bot_friend_count, get_bot_group_count
from .system import get_system_avgload, get_system_virtual_memory_percent, get_system_swap_memory_percent, get_system_uptime

status = on_command('status', rule=to_me(), priority=5)
poke = on_type(PokeNotifyEvent, rule=to_me(), priority=5)


@status.handle()
@poke.handle()
async def _(bot: Bot):
    await status.finish(await generate_status(bot))


async def generate_status(bot: Bot) -> str:
    return dedent(f'''\
        [mokabot 运行状态]
        
        已加载 {await get_bot_friend_count(bot)} 个好友，{await get_bot_group_count(bot)} 个群聊
        最后一条消息发送于：{get_last_message_time()})
        
        上线时间：
         - Bot：{get_bot_uptime()}
         - 主机：{get_system_uptime()}

        主机负载：
         - CPU：{get_system_avgload()}
         - 内存：{get_system_virtual_memory_percent()}
         - Swap：{get_system_swap_memory_percent()}
         
        统计信息：
         - 最近一分钟内收发消息总数：{message_counter.count_last_minute()}
         - 最近一小时内收发消息总数：{message_counter.count_last_hour()}
         - 最近一天内收发消息总数：{message_counter.count_last_day()}
         - 消息接收/发送总计：{get_message_received_count()} / {get_message_sent_count()}
         - WebSocket 连接断开次数：{get_disconnect_times()}''')
