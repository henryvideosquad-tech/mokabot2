from typing import Optional

import httpx


def get_client(proxies: Optional[str] = None, timeout: float = 15, retries: int = 0, **kwargs) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        proxies=proxies,
        timeout=timeout,
        transport=httpx.AsyncHTTPTransport(retries=retries) if retries else None,
        **kwargs
    )


def get_headers() -> dict[str, str]:
    return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0'}
