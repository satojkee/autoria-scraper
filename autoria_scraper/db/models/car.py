"""This module contains `Car` db model."""


from typing import Optional
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column, Mapped

from autoria_scraper.db.models._base import Base


__all__ = ('Car',)


class Car(Base):
    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    price_usd: Mapped[float] = mapped_column(nullable=False)
    odometer: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(nullable=True)
    image_url: Mapped[str] = mapped_column(nullable=True)
    images_count: Mapped[int] = mapped_column(nullable=False, default=0)
    car_number: Mapped[Optional[str]] = mapped_column(nullable=True)
    car_vin: Mapped[Optional[str]] = mapped_column(nullable=True)
    datetime_found: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
