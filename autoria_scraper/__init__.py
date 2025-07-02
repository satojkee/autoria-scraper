"""Application root package."""


from queue import Queue
from logging.handlers import QueueHandler, QueueListener
from logging import (
    StreamHandler,
    Formatter,
    getLogger,
    DEBUG
)


__all__ = ('start',)


logger = getLogger(__name__)
# use `Queue` to avoid blocking main thread with logs
log_queue = Queue()

stderr_handler = StreamHandler()
queue_handler = QueueHandler(log_queue)

stderr_handler.setFormatter(
    Formatter(
        fmt='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
)


logger.addHandler(queue_handler)
logger.setLevel(DEBUG)
# configuring `QueueListener`, it's crucial to execute `.start()` before
#  any `logging` calls
# also, don't forget to call `.stop()` to not lose anything on exit
listener = QueueListener(log_queue, stderr_handler)


async def start() -> None:
    """Entrypoint function.
    Checks database connection and starts scraping.

    :return: None
    """
    # enables listener for logging
    listener.start()

    from autoria_scraper.db.models import Car
    from autoria_scraper.db import init_db, save_multiple
    from autoria_scraper.config import app_config
    from autoria_scraper.core.scrapers import ListingScraper, DirectScraper

    # checks database connection and creates necessary tables if those missing
    await init_db()
    # processes pages with listings to obtain `direct` links
    listing_scraper = ListingScraper(
        root_url=app_config.scraper.root_url.__str__(),
        batch_size=app_config.scraper.batch_size,
        pages_limit=app_config.scraper.pages_limit
    )
    direct_links = await listing_scraper.start()
    # uses obtained links to configure `direct` scraper
    # it returns a collection of `CarParser` instances,
    #  which can be easily converted to `Car` instances
    direct_scraper = DirectScraper(
        phone_url=app_config.scraper.phone_url.__str__(),
        links=tuple(direct_links),
        batch_size=app_config.scraper.batch_size
    )
    async for data in direct_scraper.start():
        # saves data to the db
        await save_multiple([
            Car(**instance.model_dump())
            for instance in data
            if instance is not None
        ])

    # stops `QueueListener`
    listener.stop()
