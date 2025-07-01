"""This module contains `BaseParser` class, which is used to define parsers.
"""


from pydantic import BaseModel


__all__ = ('BaseParser',)


class BaseParser(BaseModel):
    """`pydantic.BaseModel` with preconfigured settings.
    Use instead of `BaseModel` for parsers.
    """

    class Config:
        arbitrary_types_allowed = True
