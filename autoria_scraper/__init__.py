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

    1. Enables queue listener for logging
    2. Checks database connection and creates necessary tables
    3. Starts crawling

    :return: None
    """
    listener.start()

    from autoria_scraper.db.models import Car
    from autoria_scraper.db import init_db, save_multiple
    from autoria_scraper.config import app_config
    from autoria_scraper.core.scrapers import CatalogScraper, DirectScraper

    # checks database connection and creates necessary tables if those missing
    await init_db()
    # processes pages with listings to obtain `direct` links
    catalog_scraper = CatalogScraper(
        root_url=app_config.scraper.root_url.__str__(),
        batch_size=app_config.scraper.batch_size,
        pages_limit=app_config.scraper.pages_limit
    )
    async for urls in catalog_scraper.start():
        # using obtained collection of urls to set up `direct` scraper
        direct_scraper = DirectScraper(
            phone_url=app_config.scraper.phone_url.__str__(),
            links=urls,
            batch_size=app_config.scraper.batch_size
        )
        async for chunk in direct_scraper.start():
            # each `chunk` is a collection of `CarParser` instances
            #  which can be easily converted to `Car` instances
            await save_multiple([
                Car(**instance.model_dump())
                for instance in chunk
                if instance is not None
            ])

    listener.stop()
