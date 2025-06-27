"""This package contains web-scrapers.

Paged scraper:
    This one is used for obtaining direct links to the listed cars.
    Then, we can use these links to set up `Direct` scraper.

Direct scraper:
    todo: add description
"""


from .direct import DirectScraper
from .listing import ListingScraper
