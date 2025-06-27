"""This module contains `Car` model parser."""


import re
from typing import Optional, Dict, Any

from bs4 import Tag
from pydantic import BaseModel, computed_field, Field


__all__ = ('CarParser',)


class CarParser(BaseModel):
    """Attributes which start with `t_` are hidden in `.model_dump()`.
    Define data parsing logic here.
    """
    t_url: str = Field(exclude=True)
    t_title: "Tag" = Field(exclude=True)
    t_price_usd: "Tag" = Field(exclude=True)
    t_odometer: "Tag" = Field(exclude=True)
    t_username: "Tag" = Field(exclude=True)
    t_phone_number: Dict[str, Any] = Field(exclude=True)
    t_image_url: "Tag" = Field(exclude=True)
    t_images_count: "Tag" = Field(exclude=True)
    t_car_number: Optional["Tag"] = Field(default=None, exclude=True)
    t_car_vin: Optional["Tag"] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed: bool = True

    @computed_field
    def url(self) -> str:
        return self.t_url

    @computed_field
    def title(self) -> str:
        return self.t_title.get_text(strip=True)

    @computed_field
    def price_usd(self) -> int:
        return int(
            ''.join(self.t_price_usd.get_text(strip=True).split(' ')[:-1])
        )

    @computed_field
    def odometer(self) -> int:
        return int(
            re
            .search(r'^\d+', self.t_odometer.get_text(strip=True))
            .group()
        ) * 1000 if [_ for _ in self.t_odometer.text if _.isnumeric()] else 0

    @computed_field
    def car_vin(self) -> Optional[str]:
        return self.t_car_vin.get_text(strip=True) if self.t_car_vin else None

    @computed_field
    def image_url(self) -> str:
        return self.t_image_url.get('srcset')

    @computed_field
    def username(self) -> str:
        return self.t_username.get_text(strip=True)

    @computed_field
    def phone_number(self) -> Optional[str]:
        try:
            return '38{}'.format(
                self.t_phone_number['additionalParams']['phoneStr']
                .replace(' ', '')
                .replace('(', '')
                .replace(')', '')
            )
        except KeyError:
            return

    @computed_field
    def images_count(self) -> int:
        return int(self.t_images_count.get_text(strip=True).split(' ')[-1])

    @computed_field
    def car_number(self) -> Optional[str]:
        if self.t_car_number:
            return ''.join(
                self.t_car_number.find_all(
                    string=True,
                    recursive=False
                )
            ).strip()
