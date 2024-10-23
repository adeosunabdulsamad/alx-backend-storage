#!/usr/bin/env python3
"""
Thi module uses the redis dbms to
create a string vlue for  a key in the
database
"""
import redis
import uuid
from typing import Union


class Cache:
    """
    Thi is the cache class
    """
    def __init__(self):
        """
        This is the initialization instance
        """
        self.__redis = redis.Redis()
        self.__redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Thi is a store instance
        """
        exercise_key = str(uuid.uuid4())
        self.__redis.set(exercise_key, data)
        return exercise_key
