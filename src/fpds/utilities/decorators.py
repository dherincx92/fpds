"""General utility decorators

author: derek663@gmail.com
last_updated: 01/15/2024
"""

import time


def timeit(func):
    def wrapper(*args, **kwargs):
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
