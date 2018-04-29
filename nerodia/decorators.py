import datetime
import functools
import warnings
from collections import OrderedDict, namedtuple
from typing import Callable


CacheValue = namedtuple("CacheValue", "value time")


def _method_cache_key_generator(*args, **kwargs) -> int:
    """A cache key generator implementation for methods.

    This generator does not implement any hashing for keyword arguments.
    Additionally, it skips the first argument provided to the function,
    which is assumed to be a class instance and not of importance for the key.

    Warnings:
        When keyword arguments are provided, outputs
        a log message with the severity `warning`.
    """

    if kwargs:
        warnings.warn(
            f"Got keyword arguments {kwargs!r}, but this key "
            "generator only supports regular arguments."
        )

    return hash(args[1:])


def timed_async_cache(
    expire_after: datetime.timedelta,
    max_size: int = 128,
    key: Callable = _method_cache_key_generator,
):
    """An asynchronous cache with value expiry.

    Must be applied on a coroutine.

    Args:
        expire_after (datetime.timedelta):
            Specifies after how much time a cache entry should
            be expired and refreshed from the decorated coroutine.
        max_size (int):
            The maximum amount of items to keep in the cache.
        key (Callable):
            A function that takes the arguments and keyword
            arguments passed to the function and generates a
            unique key for the item.
            Must return a type that can be used as a dictionary key.
    """

    cache = OrderedDict()

    def decorator(wrapped):

        @functools.wraps(wrapped)
        async def wrapper(*args, **kwargs):
            cache_key = key(*args, **kwargs)

            value = cache.get(cache_key)
            if value is None:
                if len(cache) > max_size:
                    cache.popitem(last=False)
                cache[cache_key] = CacheValue(
                    await wrapped(*args, **kwargs), datetime.datetime.utcnow()
                )

            # Check if the stored value has expired
            elif datetime.datetime.utcnow() - cache[cache_key].time > expire_after:
                cache[cache_key] = CacheValue(
                    await wrapped(*args, **kwargs), datetime.datetime.utcnow()
                )

            return cache[cache_key].value

        return wrapper

    return decorator
