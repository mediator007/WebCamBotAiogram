from functools import wraps
import time
from loguru import logger


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, time_monitoring=None):
    backoff.counter = 0
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            while True:
                try:
                    t = start_sleep_time * (factor**backoff.counter)
                    if t > border_sleep_time:
                        t = border_sleep_time
                    time.sleep(t)
                    if time_monitoring:
                        logger.warning(f"Delay to restart {func.__name__}: {t}s")
                    return func(*args, **kwargs)

                except Exception as exc:
                    logger.error(f"Problem with {func.__name__}: {exc}")
                    backoff.counter += 1
                    continue
                break
                
        return inner

    return func_wrapper


if __name__ == '__main__':
    
    logger.add("debug.log", format="{time} {level} {message}", level="INFO", rotation="1 MB")
    @backoff(time_monitoring=True)
    def print_func():
        print("Try to connect...")
        a = 1 / 0
        print(a)

    print_func()