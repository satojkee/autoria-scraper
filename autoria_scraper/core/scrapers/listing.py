"""This module contains `Listing` web-scraper.

This one is used for obtaining direct links to the listed cars.

Examples:
    https://auto.ria.com/uk/auto_mercedes_benz_sprinter_38472224.html
    https://auto.ria.com/uk/auto_skoda_fabia_38504178.html
    https://auto.ria.com/uk/auto_toyota_land_cruiser_37252171.html
"""


from typing import Coroutine, Optional

from autoria_scraper.core.selectors import (
    ListedSelectors,
    PaginationSelectors
)
from autoria_scraper.core.misc import fetch_soup
from autoria_scraper.core.scrapers._base import BaseScraper


__all__ = ('ListingScraper',)


class ListingScraper(BaseScraper):
    """This scraper is used for obtaining direct links to the listed items"""

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
        self._direct_links = set()

        self._logger.debug('initialized, root: %s', self._root)

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

    async def __extract_links(self, url: str) -> None:
        """This method extracts direct link for each listed car.
        Then pushes extracted links to the `self._direct_links` set.

        :param url: str - listing url, e.g: https://autoria.com/.../?page=1
        :return: None
        """
        response = await fetch_soup(url=url)
        # find all direct links and push them to the set
        self._direct_links.update([
            link.get('href')
            for link in response.find_all(**ListedSelectors.link)
        ])

    async def __process_listings(self, total_pages: int) -> None:
        """This method gathers `__extract_links` tasks.

        ! Select the batch size depending on your RAM amount,
        the higher this value is, the more RAM will be consumed.

        :return: None
        """

        def func_(s: int, e: int) -> list[Coroutine]:
            """Function to use in `self._process_range` as `func` param.

            :param s: int - start index
            :param e: int - end index
            :return: list[Coroutine]
            """
            return [
                self.__extract_links(f'{self._root}?page={_}')
                for _ in range(s, e)
            ]

        from_ = 1
        for to_ in range(self._batch_size, total_pages + 1, self._batch_size):
            # concurrent processing, tasks amount = batch size
            await self._process_range(s=from_, e=to_, func=func_)
            # updates `previous` value, 0-10 -> 10-20 (step = batch size)
            from_ = to_
            # displays the current amount of extracted urls
            self._logger.debug('urls obtained: %d', len(self._direct_links))
        # similar to the last range (from_:total_pages + 1)
        await self._process_range(s=from_, e=total_pages + 1, func=func_)

    async def start(self) -> list:
        """This method starts the web-scraping process.

        Obtains the total amount of pages and processes them concurrently.
        Each page contains up to 100 listed cars. (99% - 20 cars per page)

        :return: list - a list of extracted urls
        """
        pages_count = await self.__count_pages()
        # answers: how many pages with listings?
        self._logger.info('pages discovered: %d', pages_count)
        # now, it's crucial to extract direct link for each listed car
        await self.__process_listings(pages_count)
        # displays amount of extracted urls
        self._logger.info(
            'processing completed, total urls: %d',
            len(self._direct_links)
        )
        # AutoRia is lowkey a mess, so we have to filter out "newauto" links
        # being in the /used/ section doesn't make any sense here :c
        return [_ for _ in self._direct_links if '/newauto/' not in _]
