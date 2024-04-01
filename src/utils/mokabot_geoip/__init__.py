import json
from ipaddress import IPv4Address, IPv6Address, AddressValueError
from typing import Optional

from httpx import AsyncClient, AsyncHTTPTransport
from pydantic import BaseModel

from .model import UserAgentInfoResponse, IpApiResponse, Mir6Response


def get_client(proxies: Optional[str] = None, timeout: float = 15, retries: int = 0, **kwargs) -> AsyncClient:
    return AsyncClient(
        proxies=proxies,
        timeout=timeout,
        transport=AsyncHTTPTransport(retries=retries) if retries else None,
        **kwargs
    )


def jsonp_to_json(jsonp: str) -> dict:
    start = jsonp.find('(')
    end = jsonp.rfind(')')
    json_str = jsonp[start + 1:end]
    return json.loads(json_str)


def is_valid_ip(ip: str) -> bool:
    return is_valid_ipv4(ip) or is_valid_ipv6(ip)


def is_valid_ipv4(ip: str) -> bool:
    try:
        IPv4Address(ip)
        return True
    except AddressValueError:
        return False


def is_valid_ipv6(ip: str) -> bool:
    try:
        IPv6Address(ip)
        return True
    except AddressValueError:
        return False


class BaseGeoIPLookup(object):

    async def lookup(self, ip: str) -> BaseModel:
        raise NotImplementedError


class GeoIPLookupIPAPI(BaseGeoIPLookup):
    """ip-api.com"""

    async def lookup(self, ip: str) -> IpApiResponse:
        async with get_client() as client:
            response = await client.get(f'http://ip-api.com/json/{ip}?lang=zh-CN&fields=4255711')

        return IpApiResponse(**response.json())


class UserAgentInfoAPI(BaseGeoIPLookup):
    """ip.useragentinfo.com. It is more accurate when querying China’s domestic IP information """

    async def lookup(self, ip: str) -> UserAgentInfoResponse:
        async with get_client() as client:
            response = await client.get(f'https://ip.useragentinfo.com/jsonp?ip={ip}')
            jsonp_response = response.text
            json_response = jsonp_to_json(jsonp_response)

        return UserAgentInfoResponse(**json_response)


class Mir6API(BaseGeoIPLookup):
    """api.mir6.com IPv4, IPv6 or domain"""

    async def lookup(self, ip: str) -> Mir6Response:
        async with get_client() as client:
            response = await client.get(f'https://api.mir6.com/api/ip?ip={ip}&type=json')

        return Mir6Response(**response.json())


ipapi = GeoIPLookupIPAPI()
uainfo = UserAgentInfoAPI()
mir6 = Mir6API()
