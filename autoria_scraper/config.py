"""This module contains app configuration."""


import sys
from typing import Optional
from logging import getLogger

from pydantic import (
    BaseModel,
    ValidationError,
    PostgresDsn,
    HttpUrl,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


__all__ = ('app_config',)


class Database(BaseModel):
    """Contains database settings."""
    url: PostgresDsn


class AioHttp(BaseModel):
    """Contains aiohttp settings."""
    attempts_limit: int
    attempt_delay: float
    timeout: int


class Scraper(BaseModel):
    """Contains web-scraper settings."""
    root_url: HttpUrl
    phone_url: HttpUrl
    batch_size: int
    pages_limit: Optional[int] = None


class Settings(BaseSettings):
    database: Database
    scraper: Scraper
    aiohttp: AioHttp

    model_config = SettingsConfigDict(
        env_file=('.env.local', '.env'),
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        extra='ignore'
    )


logger = getLogger(__name__)

try:
    app_config = Settings()
except ValidationError as e:
    logger.error('validation error during config initialization: %s', e)

    sys.exit(-1)
