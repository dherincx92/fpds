"""General utility decorators

author: derek663@gmail.com
last_updated: 01/15/2024
"""

import time


def standardize_format(seconds: int) -> str:
    minutes = int(seconds / 60)
    _seconds = int(seconds % 60)
    return f"{minutes}:{_seconds}"


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        formatted_time = standardize_format(execution_time)
        print(f"{func.__name__} took {formatted_time} seconds to run.")
        return result

    return wrapper
