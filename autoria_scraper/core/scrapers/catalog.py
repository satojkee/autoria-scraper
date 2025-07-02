"""This module contains `CatalogScraper` class."""


from logging import getLogger
from itertools import chain
from typing import (
    Coroutine,
    Optional,
    List,
    AsyncGenerator,
    Tuple
)

from autoria_scraper.core.selectors import (
    ListedSelectors,
    PaginationSelectors
)
from autoria_scraper.core.misc import (
    fetch_soup,
    chunked_range_processing
)
from autoria_scraper.core.scrapers._base import BaseScraper


__all__ = ('CatalogScraper',)


logger = getLogger(__name__)


class CatalogScraper(BaseScraper):
    """This scraper is used for catalog processing in order to obtain
     the collection of `direct` urls.
    """

    def __init__(
        self,
        root_url: str,
        batch_size: int,
        pages_limit: Optional[int] = None
    ) -> None:
        """
        :param root_url: str - base url for web-scraping
        :param batch_size: int - batch size for concurrent processing
        :param pages_limit: Optional[int] - limits the amount of pages
         (for testing purposes)
        :return: None
        """
        super().__init__()

        self._root = root_url
        self._batch_size = batch_size
        self._pages_limit = pages_limit
        # each item in this set is a https link to the listed car on AutoRia
        # it's used to avoid duplicates
        self._url_pool = set()

    async def __count_pages(self) -> int:
        """Use this method to obtain the total amount of pages.

        :return: int - number of pages
        """
        if self._pages_limit is not None:
            return self._pages_limit

        response = await fetch_soup(url=self._root)
        # AutoRia pagination has a hidden link widget
        # text of that link follows format: '{current_page} / {total_pages}'
        # example: "1 / 18 100", so we have to parse it
        # split string by '/' and take the last element, in result: " 18 100"
        # then replace spaces with "" and convert that value to int
        return int(
            response
            .find(**PaginationSelectors.container)
            .find(**PaginationSelectors.link)
            .get_text(strip=True)
            .split('/')[-1]
            .replace(' ', '')
        )

    async def __extract_links(self, url: str) -> List[str]:
        """This method processes page context to obtain the collection
         of valid "direct" urls. Extends `self._url_pool` set with collected
         urls and returns them as list. Also, removes links which contain
         '/newauto/' keyword.

        :param url: str - listing url, e.g: https://autoria.com/.../?page=1
        :return: List[str] - the list of valid urls
        """
        response = await fetch_soup(url=url)
        # applies `.get('href')` method for each tag element
        # and returns only those that are not in the `self._url_pool` set
        #  and do not contain '/newauto/' keyword
        urls = [
            url
            for url in map(lambda tag: tag.get('href'),
                           response.find_all(**ListedSelectors.link))
            if url not in self._url_pool and '/newauto/' not in url
        ]
        # pushes extracted urls to the pool (crucial to avoid duplicates)
        self._url_pool.update(urls)

        return urls

    async def start(self) -> AsyncGenerator[Tuple[str], None]:
        """This method starts the web-scraping process.

        **Usage example**

        ```python
        scraper = CatalogScraper(...)

        async for urls in scraper.start():
            print(urls) # Collection[str]
        ```

        :return: AsyncGenerator[Collection[str], None]
        """

        def func_(s: int, e: int) -> List[Coroutine]:
            """Returns a list of coroutines for concurrent processing.

            :param s: int - start index
            :param e: int - end index
            :return: List[Coroutine]
            """
            return [
                self.__extract_links(f'{self._root}?page={_}')
                for _ in range(s, e)
            ]

        pages_count = await self.__count_pages()

        logger.info('pages discovered: %d', pages_count)

        async for chunk in chunked_range_processing(
            func=func_,
            from_=1,
            to_=pages_count + 1,
            batch=self._batch_size
        ):
            # using `itertools.chain` to flatten the response
            # example: [[1, 2], [3, 4]] -> [1, 2, 3, 4]
            yield tuple(chain(*chunk))
