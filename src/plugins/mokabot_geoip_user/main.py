from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from src.utils.mokabot_geoip import is_valid_ip, ipapi, uainfo, mir6

ip_query = on_command('ip', priority=5)


@ip_query.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    query = args.extract_plain_text().strip()

    if not query or not is_valid_ip(query):
        await matcher.finish('请输入有效的 IP 地址')

    result_ipapi = await ipapi.lookup(query)
    result_uainfo = await uainfo.lookup(query)
    result_mir6 = await mir6.lookup(query)

    msg = f'Query: {query}\nipapi: {result_ipapi}\nuainfo: {result_uainfo}\nmir6: {result_mir6}'

    await matcher.finish(msg, reply_message=True)
