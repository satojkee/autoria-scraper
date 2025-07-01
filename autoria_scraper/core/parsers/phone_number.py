"""This module contains `PhoneNumberParser`."""


import re

from bs4 import Tag
from pydantic import computed_field, Field

from ._base import BaseParser


__all__ = ('PhoneNumberParser',)


class PhoneNumberParser(BaseParser):
    """Attributes which start with `t_` are hidden in `.model_dump()`.
    Define data parsing logic here.
    """
    t_auto_id: "Tag" = Field(exclude=True)
    t_phone_id: "Tag" = Field(exclude=True)
    t_user_id: str = Field(exclude=True)

    @computed_field
    def auto_id(self) -> str:
        return self.t_auto_id.get('data-auto-id')

    @computed_field
    def phone_id(self) -> str:
        return self.t_phone_id.get('data-value-id')

    @computed_field
    def user_id(self) -> str:
        return (
            re
            .search(r'data-owner-id="(\d*)"', self.t_user_id)
            .group(1)
        )
