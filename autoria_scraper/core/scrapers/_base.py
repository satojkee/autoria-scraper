"""This module contains a `BaseScraper` class."""


import asyncio
from logging import getLogger
from typing import Any, Callable, Tuple
from abc import ABC, abstractmethod


__all__ = ('BaseScraper',)


class BaseScraper(ABC):
    """Base class for all scrapers."""
    def __init__(self) -> None:
        self._logger = getLogger(__name__).getChild(self.__class__.__name__)

    @abstractmethod
    async def start(self) -> Any:
        """Entrypoint of each scraper."""

    async def _process_range(
        self,
        s: int,
        e: int,
        func: Callable
    ) -> Tuple[Any]:
        """Uses asyncio to spawn a list of tasks.

        :param s: int - first page index
        :param e: int - last page index
        :param func: Callable - function, that returns a list of `Coroutine`
        :return: Tuple[Any]
        """
        self._logger.info('processing range: %d - %d', s, e)
        # concurrently executes a list of tasks
        return await asyncio.gather(*func(s, e))
