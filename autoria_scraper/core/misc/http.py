"""This module contains `aiohttp` wrappers."""


import asyncio
from logging import getLogger
from functools import wraps
from typing import Callable, Any, Optional, Dict

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from aiohttp import ClientSession, ClientTimeout

from autoria_scraper.config import app_config


__all__ = ('fetch_soup', 'post')


# delay after each reattempt in `_aiohttp_session` (on failure)
_REATTEMPT_DELAY: float = app_config.scraper.aiohttp.attempt_delay
# number of reattempts for each request (on failure)
_REATTEMPTS_LIMIT: int = app_config.scraper.aiohttp.attempts_limit
# if a request exceeds that value, a `TimeoutError` will be raised
# default value provided by aiohttp is 60 * 5 = 300sec
# usually, it's faster to make a new request, than wait 5 minutes...
_timeout = ClientTimeout(total=app_config.scraper.aiohttp.timeout)
# using `fake-useragent` package to rotate user-agents
_ua = UserAgent()

logger = getLogger(__name__)


def _aiohttp_session(
    attempts: int = _REATTEMPTS_LIMIT,
    delay: float = _REATTEMPT_DELAY
) -> Callable:
    """Starts a new properly-configured `aiohttp.ClientSession`.
    Injects this session as keyword argument to the decorated function.

    :param attempts: int - number of reattempts
    :param delay: float - delay before each reattempt in seconds
    :return: Callable
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            async with ClientSession(
                headers={'User-Agent': _ua.chrome},
                timeout=_timeout
            ) as session:
                for attempt in range(attempts):
                    # if OK, breaks the loop with `return` statement
                    # if failed -> next iteration
                    try:
                        return await func(session=session, *args, **kwargs)
                    except Exception as e:
                        # 1. current attempt
                        # 2. total attempts
                        # 3. function name
                        # 4. exception message or `timeout` for `TimeoutError`
                        # 5. failed function args
                        # 6. failed function kwargs
                        logger.warning(
                            'aiohttp request failed, attempt: %d of %d, '
                            'func: [%s], reason: "%s", args: %s, kwargs: %s',
                            attempt + 1,
                            attempts,
                            func.__name__,
                            e
                            if not isinstance(e, TimeoutError)
                            else 'timeout',
                            args,
                            kwargs
                        )
                    # delay before each reattempt
                    await asyncio.sleep(delay)

        return wrapper
    return decorator


@_aiohttp_session()
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


@_aiohttp_session()
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
