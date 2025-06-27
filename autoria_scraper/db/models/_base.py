"""This module contains the `Base` model class."""


from sqlalchemy.orm import DeclarativeBase


__all__ = ('Base',)


class Base(DeclarativeBase):
    """Base class used for declarative class definitions."""
