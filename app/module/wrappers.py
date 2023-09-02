import asyncio
from functools import wraps


def async_wrapper_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, func, *args, **kwargs)
        return result
    return wrapper
