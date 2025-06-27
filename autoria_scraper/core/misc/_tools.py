"""This module contains useful tools."""


import asyncio
from functools import wraps
from logging import getLogger
from typing import Callable, Any

from autoria_scraper.config import app_config


__all__ = ('retry_on_failure',)


logger = getLogger(__name__)


_REATTEMPT_DELAY: float = app_config.scraper.aiohttp.attempt_delay
_REATTEMPTS_LIMIT: int = app_config.scraper.aiohttp.attempts_limit


def retry_on_failure(
    attempts: int = _REATTEMPTS_LIMIT,
    delay: float = _REATTEMPT_DELAY
) -> Callable:
    """Use this decorator to restart any async function on its failure.

    :param attempts: int - number of reattempts
    :param delay: float - delay before each reattempt
    :return: Callable
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for _ in range(attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.warning(
                        'retry on failure, '
                        'func: [%s], reason: "%s", args: %s, kwargs: %s',
                        func.__name__,
                        e if not isinstance(e, TimeoutError) else 'timeout',
                        args,
                        kwargs
                    )
                # delay before each reattempt
                await asyncio.sleep(delay)

            logger.error('')

        return wrapper
    return decorator
