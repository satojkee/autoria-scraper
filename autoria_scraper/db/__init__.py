"""This package contains db-related stuff."""


import sys
from typing import Collection
from logging import getLogger

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from autoria_scraper.config import app_config
from autoria_scraper.db.models import Base


__all__ = ('init_db', 'save_multiple')


logger = getLogger(__name__)

engine = create_async_engine(url=app_config.database.url.__str__())
# using `sessionmaker` for automatic configuration of new sessions
SessionFactory = async_sessionmaker(bind=engine, expire_on_commit=True)


async def init_db() -> None:
    """This function checks the connection and creates necessary tables
        if they don't exist.

    :return: None
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.error('connection error: %s', e)

        sys.exit(-1)


async def save_multiple(data: Collection["Base"]) -> None:
    """This function saves a list of instance to the db.

    :param data: Collection["Base"] - the collection of instances
    :return: None
    """
    async with SessionFactory() as session:
        try:
            session.add_all(data)

            await session.commit()
            # `success` log-message with number of items saved
            logger.info('transaction succeeded, items: [%s]', len(data))
        except Exception as e:
            logger.error('transaction failed, reason: %s', e)

            await session.rollback()
