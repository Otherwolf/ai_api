from time import perf_counter

from system.module.logger import getlogger

logger = getlogger('profiler')


def profiler(func):
    def wrapper(*args, **kwargs):
        before = perf_counter()
        retval = func(*args, **kwargs)
        after = perf_counter()
        logger.warning(f"{func.__name__}: time={after-before}")
        return retval

    return wrapper
