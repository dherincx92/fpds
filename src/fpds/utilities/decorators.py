"""
General utility decorators

author: derek663@gmail.com
last_updated: 2024/07/03
"""

import time


def timeit(func):  # type: ignore
    def wrapper(*args, **kwargs):  # type: ignore
        start_time = time.time()
        print("Transforming XML into JSON...")
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(
            f"`{func.__name__}` took {round(duration / 60, 3)} minutes to run..."
            f"{len(result)} records extracted!"
        )
        return result

    return wrapper
