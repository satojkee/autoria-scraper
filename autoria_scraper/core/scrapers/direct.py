"""This module contains `DirectScraper` class.

This one is used for data extraction from direct links.
"""


from typing import (
    Any,
    Collection,
    Coroutine,
    Dict,
    Optional,
    List,
    AsyncGenerator
)

from autoria_scraper.core.misc import fetch_soup, post
from autoria_scraper.core.selectors import CarSelectors
from autoria_scraper.core.scrapers._base import BaseScraper
from autoria_scraper.core.parsers import CarParser, PhoneNumberParser


__all__ = ('DirectScraper',)


class DirectScraper(BaseScraper):
    def __init__(
        self,
        phone_url: str,
        links: Collection[str],
        batch_size: int
    ) -> None:
        """
        :param phone_url: str - required for obtaining sellers' phone numbers
        :param links: Collection[str] - collection of direct links
        :param batch_size: int - batch size for concurrent processing
        :return: None
        """
        super().__init__()

        self._phone_url = phone_url
        self._links = links
        self._batch_size = batch_size

    async def __extract_data(self, url: str) -> "CarParser":
        """This method extract all necessary data from the given url.

        Collects:
            - vin
            - title
            - username
            - price
            - odometer
            - number
            - images count
            - primary image url
            - phone number

        :param url: str - direct link to the car
        :return: CarParser - parsed data instance
        """

        async def _obtain_phone_number(
            pnp: "PhoneNumberParser"
        ) -> Optional[Dict[str, Any]]:
            """Makes some manipulations to obtain seller's phone number.
            In order to obtain seller phone number, we have to make a POST
            request on https://auto.ria.com/bff/final-page/public/auto/popUp/

            **Request body example**

            ```json
            {
              "autoId": 38330999,
              "blockId": "autoPhone",
              "data": [
                ["userId", "4745906"],
                ["phoneId", "682365827"]
              ]
            }
            ```

            :param pnp: PhoneNumberParser - parsed pieces of phone number
            :return: Optional[Dict[str, Any]] - json response to parse
            """
            return await post(
                url=self._phone_url,
                json={
                    'autoId': pnp.auto_id,
                    'blockId': 'autoPhone',
                    'data': [
                        ['userId', pnp.user_id],
                        ['phoneId', pnp.phone_id]
                    ]
                },
                headers={'Content-Type': 'application/json'}
            )

        response = await fetch_soup(url)
        # first of all, we've to check the availability of the car
        # in some cases, car's page is accessible, but still not listed
        #  (doesn't have any data) and the following message appears:
        #  "Оголошення ... ще не опубліковане і не бере участі в пошуку"
        # so, we've to check the presence of specific tag `car_unavailable`
        # and if it's present -> skip
        if response.find(**CarSelectors.unavailable) is None:
            _checked_vin = response.find(**CarSelectors.vin_checked)
            _unchecked_vin = response.find(**CarSelectors.vin_unchecked)
            # sometimes `car_vin` may be absent in the regular place
            # we choose between `_checked_vin` and `_unchecked_vin`
            # None value is still possible, but it's OK
            car_vin = _checked_vin or _unchecked_vin
            user_id = response.__str__()
            auto_id = response.find(**CarSelectors.phone_number_auto_id)
            phone_id = response.find(**CarSelectors.phone_number_phone_id)
            car_number = response.find(**CarSelectors.state_number)
            title = response.find_all(**CarSelectors.title)[-1]
            username = response.find(**CarSelectors.username)
            odometer = response.find(**CarSelectors.odometer)
            primary_image = response.find_all(**CarSelectors.image_url)[1]
            price_usd = (
                response
                .find(**CarSelectors.price_container)
                .find(**CarSelectors.price)
            )
            images_count = (
                response
                .find_all(**CarSelectors.images_count_container)
                [0]
                .find(**CarSelectors.images_count)
            )
            phone_number = await _obtain_phone_number(
                PhoneNumberParser(
                    t_auto_id=auto_id,
                    t_phone_id=phone_id,
                    t_user_id=user_id
                )
            )
            # now, parse the data using `pydantic` features
            # `.model_dump()` returns a valid dict with all necessary fields
            #  in proper format
            parsed_entity = CarParser(
                t_url=url,
                t_car_vin=car_vin,
                t_title=title,
                t_username=username,
                t_price_usd=price_usd,
                t_odometer=odometer,
                t_car_number=car_number,
                t_image_url=primary_image,
                t_images_count=images_count,
                t_phone_number=phone_number
            )

            self._logger.info('received: %s', parsed_entity.model_dump())

            return parsed_entity
        else:
            self._logger.info('data unavailable, skipping: %s', url)

    async def start(
        self
    ) -> AsyncGenerator[Collection[Optional["CarParser"]], None]:
        """This method starts the web-scraping process.

        **Usage example**
        ```python
        scraper = DirectScraper(...)

        async for chunk in scraper.start():
            print(chunk) # Collection[Optional["CarParser"]]
        ```
        :return: AsyncGenerator[Collection[Optional["CarParser"]], None]
        """

        def func_(s: int, e: int) -> List[Coroutine]:
            """Function to use in `self._process_range` as `func` param.

            :param s: int - start index
            :param e: int - end index
            :return: list[Coroutine]
            """
            return [self.__extract_data(link) for link in self._links[s:e]]

        from_ = 0
        for to_ in range(self._batch_size,
                         len(self._links) + 1,
                         self._batch_size):
            # concurrent processing, tasks amount = batch_size
            yield await self._process_range(s=from_, e=to_, func=func_)
            # move to the next range of links, 0-10 -> 10:20
            from_ = to_
        # processing the last range (from_:last_index + 1)
        yield await self._process_range(s=from_,
                                        e=len(self._links),
                                        func=func_)
