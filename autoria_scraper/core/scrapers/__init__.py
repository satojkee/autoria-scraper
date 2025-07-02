"""This package contains web-scrapers.

Catalog scraper:
    This one is used for obtaining "direct" links to the listed cars.
    Then, we can use these links to set up `Direct` scraper.

    **Usage example**

    ```python
    catalog_scraper = CatalogScraper(
        root_url=...,
        batch_size=...,
        **kwargs
    )

    async for urls in catalog_scraper.start():
        print(urls) # Tuple[str]
    ```

Direct scraper:
    Extracts necessary information from each "direct" link (1 link = 1 car).
    Yields a collection of `CarParser` instances (each `CarParser` instance
     can be easily converted to `Car` instance)

    **Usage example**

    ```python
    direct_scraper = DirectScraper(
        phone_url=...
        links=...,
        batch_size=...
    )

    async for chunk in direct_scraper.start():
        print(chunk) # Tuple[Optional["CarParser"]]
    ```
"""


from .direct import DirectScraper
from .catalog import CatalogScraper
