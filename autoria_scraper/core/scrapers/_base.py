"""This module contains a `BaseScraper` class."""


import asyncio
from logging import getLogger
from abc import ABC, abstractmethod
from typing import Any, Collection, Tuple, Coroutine


__all__ = ('BaseScraper',)


class BaseScraper(ABC):
    """Base class for all scrapers."""

    def __init__(self) -> None:
        self._logger = getLogger(__name__).getChild(self.__class__.__name__)

    @abstractmethod
    async def start(self) -> Any:
        """Entrypoint of each scraper."""

    async def _concurrent_processing(
        self,
        tasks: Collection[Coroutine]
    ) -> Tuple[Any]:
        """Uses asyncio to process multiple tasks concurrently.
        Wraps `asyncio.gather` function with additional logging.

        :param tasks: Collection[Coroutine] - a collection of coroutines
        :return: Tuple[Any]
        """
        self._logger.debug('spawning %d tasks', len(tasks))
        # returns a tuple of results
        return await asyncio.gather(*tasks)
