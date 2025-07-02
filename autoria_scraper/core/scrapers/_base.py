"""This module contains a `BaseScraper` class."""


from typing import Any
from abc import ABC, abstractmethod


__all__ = ('BaseScraper',)


class BaseScraper(ABC):
    """Base class for all scrapers."""

    @abstractmethod
    async def start(self) -> Any:
        """Entrypoint of each scraper."""
