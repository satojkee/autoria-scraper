"""This module contains `aiohttp` wrappers."""


from functools import wraps
from typing import Callable, Any, Optional, Dict

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from aiohttp import ClientSession, ClientTimeout

from autoria_scraper.config import app_config
from autoria_scraper.core.misc._tools import retry_on_failure


__all__ = ('fetch_soup', 'post')


# if a request exceeds that value, a `TimeoutError` will be raised
# default value provided by aiohttp is 60 * 5 = 300sec
# usually, it's faster to make a new request, than wait 5 minutes...
_timeout = ClientTimeout(total=app_config.scraper.aiohttp.timeout)
# using `fake-useragent` package to rotate user-agents
_ua = UserAgent()


def _aiohttp_session(func: Callable) -> Callable:
    """Starts a new properly-configured `aiohttp.ClientSession`.
    Injects this session as keyword argument to the decorated function.

    :param func: Callable - targeted function
    :return: Callable
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async with ClientSession(
            headers={'User-Agent': _ua.chrome},
            timeout=_timeout
        ) as session:
            return await func(session=session, *args, **kwargs)
    return wrapper


@retry_on_failure()
@_aiohttp_session
async def fetch_soup(
    url: str,
    session: "ClientSession",
) -> Optional["BeautifulSoup"]:
    """This function makes a GET request to a given url and returns
        its response as `BeautifulSoup` instance.

    :param session: ClientSession - automatically injected
    :param url: str - targeted url
    :return: Optional[BeautifulSoup] - `BeautifulSoup` instance
        if OK, else None
    """
    async with session.get(url) as response:
        return BeautifulSoup(
            markup=await response.content.read(),
            features='lxml'
        )


@retry_on_failure()
@_aiohttp_session
async def post(
    url: str,
    session: "ClientSession",
    **kwargs: Any
) -> Optional[Dict[str, Any]]:
    """This function makes a POST request to a given url and returns
        its response as `json` (dict).

    :param url: str - targeted url
    :param session: ClientSession - automatically injected
    :param kwargs: Any - additional keyword params supported by `aiohttp.post`
    :return: Optional[Dict[str, Any]] - json response if OK, else None
    """
    async with session.post(url, **kwargs) as response:
        return await response.json()
