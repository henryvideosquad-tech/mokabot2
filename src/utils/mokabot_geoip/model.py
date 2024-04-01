from datetime import datetime
from re import match
from typing import Optional, Union

from pydantic import BaseModel, Field


def join_only_valid_fields(fields: list[str]) -> str:
    return ' '.join(field for field in fields if field)


def extract_asn(asn: str) -> tuple[Optional[str], Optional[str]]:
    # AS20473 The Constant Company, LLC -> ('AS20473', 'The Constant Company, LLC')
    if not asn:
        return None, None

    result = match(r'(AS\d+) (.+)', asn)
    if result:
        return result.group(1), result.group(2)
    else:
        return None, None


class IpApiResponse(BaseModel):
    # http://ip-api.com/json/xxx.xxx.xxx.xxx?lang=zh-CN&fields=4255711
    status: Optional[str] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None
    region: Optional[str] = None
    regionName: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: Optional[str] = None
    isp: Optional[str] = None
    org: Optional[str] = None
    as_: Optional[str] = Field(None, alias='as')
    asname: Optional[str] = None
    query: Optional[str] = None

    def __str__(self) -> str:
        as_number, _ = extract_asn(self.as_)
        return join_only_valid_fields([self.country, self.regionName, self.city, self.org, as_number])


class UserAgentInfoResponse(BaseModel):
    # https://ip.useragentinfo.com/json?ip=xxx.xxx.xxx.xxx (IPv4 only)
    country: Optional[str] = None
    short_name: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    area: Optional[str] = None
    isp: Optional[str] = None
    net: Optional[str] = None
    ip: Optional[str] = None
    code: Optional[int] = None
    desc: Optional[str] = None

    def __str__(self) -> str:
        return join_only_valid_fields([self.country, self.province, self.city, self.area, self.isp, self.net])


class Mir6Response(BaseModel):
    # https://api.mir6.com/api/ip?ip=xxx.xxx.xxx.xxx&type=json
    class Data(BaseModel):
        ip: Optional[str]
        dec: Optional[str]
        country: Optional[str]
        countryCode: Optional[str]
        province: Optional[str]
        city: Optional[str]
        districts: Optional[str]
        idc: Optional[str]
        isp: Optional[str]
        net: Optional[str]
        zipcode: Optional[str]
        areacode: Optional[str]
        protocol: Optional[str]
        location: Optional[str]
        myip: Optional[str]
        time: Optional[datetime]

    code: Optional[int] = None
    msg: Optional[str] = None
    data: Union[Data, list, None] = None

    def __str__(self) -> str:
        if not self.data:
            return ''
        return join_only_valid_fields(
            [self.data.country, self.data.province, self.data.city, self.data.districts, self.data.isp, self.data.net]
        )
