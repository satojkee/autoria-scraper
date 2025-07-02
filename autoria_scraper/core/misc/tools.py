"""This module contains useful functions."""


from asyncio import gather
from typing import Any, AsyncGenerator, Callable


__all__ = ('chunked_range_processing',)


async def chunked_range_processing(
    func: Callable,
    from_: int,
    to_: int,
    batch: int
) -> AsyncGenerator[Any, None]:
    """This function is used to execute multiple tasks concurrently.

    ! if the difference value between `to_` and `from_` is less than `batch`
     value, the batch size will be reduced to this difference value

    ! Raises `ValueError` if `to_` <= `from_`

    ! `func` should receive two positional arguments: `from` and `to`

    :param func: Callable - function, that takes `start:int` and `end:int`
     params and returns a list of coroutines
    :param from_: int - range from
    :param to_: int - range to
    :param batch: int - batch size
    :return: AsyncGenerator[Any, None]
    """
    if to_ <= from_:
        raise ValueError(f'bad range params: from = {from_}, to = {to_}')
    # batch size is reduced in case its value is greater than
    # the difference between `to_` and `from_`
    batch = min(batch, to_ - from_)
    for i in range(from_, to_, batch):
        end = min(i + batch, to_)
        # yields a tuple of results
        yield await gather(*func(i, end))
