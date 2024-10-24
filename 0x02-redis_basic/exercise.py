#!/usr/bin/env python3
"""
This module provides a Cache class that interacts with Redis.
"""
import redis
import uuid
import functools
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of times a method is called.
    The count is stored in Redis using the method's qualified name.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to increment the call count and call the original method.
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    
    return wrapper


class Cache:
    """
    Cache class to store and retrieve data from Redis with random keys.
    """
    def __init__(self):
        """
        Initialize Redis client and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated key.
        Args:
            data: The data to be stored, can be a string, bytes, int, or float.
        Returns:
            The key (UUID) under which the data is stored as a string.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None):
        """
        Retrieve data from Redis and optionally apply a conversion function.
        Args:
            key: The key for which to retrieve the value from Redis.
            fn: Optional. A callable to convert the data to a specific format.
        Returns:
            The retrieved value, converted by fn if provided, or raw data.
        """
        data = self._redis.get(key)

        if data is None:
            return None

        if fn is not None:
            return fn(data)

        return data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve data as a UTF-8 decoded string.
        Args:
            key: The key for which to retrieve the value from Redis.
        Returns:
            The value as a decoded string or None if the key does not exist.
        """
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve data as an integer.
        Args:
            key: The key for which to retrieve the value from Redis.
        Returns:
            The value as an integer or None if the key does not exist.
        """
        return self.get(key, fn=int)
