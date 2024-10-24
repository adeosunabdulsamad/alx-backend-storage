#!/usr/bin/env python3
"""
this is the web module
"""
import redis
import requests
from typing import Callable


r = redis.Redis()


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of times a URL is accessed.
    The count is stored in Redis using the key "count:{url}".
    """
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")
        return method(url)
    return wrapper


@count_calls
def get_page(url: str) -> str:
    """
    Get the HTML content of a URL and cache it in Redis.
    Args:
        url: The URL to fetch.
    Returns:
        The HTML content of the URL.
    """
    cached_page = r.get(f"cached:{url}")
    if cached_page:
        return cached_page.decode('utf-8')

    response = requests.get(url)
    content = response.text

    r.setex(f"cached:{url}", 10, content)

    return content
