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
        Wrapper function to increment call count and call original method.
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a method.
    The inputs and outputs are stored in two separate Redis lists.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to store inputs and outputs in Redis.
        """
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"

        self._redis.rpush(input_key, str(args))

        output = method(self, *args, **kwargs)

        self._redis.rpush(output_key, str(output))

        return output

    return wrapper


def replay(method: Callable):
    """
    Display the history of calls for a particular method.
    The inputs and outputs are retrieved from Redis and formatted.
    """
    redis_instance = method.__self__._redis
    method_name = method.__qualname__

    input_key = method_name + ":inputs"
    output_key = method_name + ":outputs"

    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)

    call_count = len(inputs)
    print(f"{method_name} was called {call_count} times:")

    for input_data, output_data in zip(inputs, outputs):
        print(f"{method_name}(*{input_data.decode('utf-8')}) -> {output_data.decode('utf-8')}")


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
    @call_history
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
