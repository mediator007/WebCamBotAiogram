from functools import lru_cache, wraps
from datetime import datetime, timedelta
import gspread
from utils.config1 import main_file, registration_file


def timed_lru_cache(seconds: int, maxsize: int = 128):
    """

    :param seconds:
    :param maxsize:
    :return:
    """
    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


@timed_lru_cache(60)
def parsing_id() -> list:
    """
    Возвращает список id из файла регистрации
    """
    gc = gspread.service_account(filename="webcambot-ad6a9a73eef6.json")
    # remove to .env
    sh = gc.open(registration_file)
    worksheet = sh.sheet1
    result = worksheet.get_all_records(expected_headers=())
    return result


@timed_lru_cache(60)
def parsing_doc():
    """
    Возвращает все записи из документа
    """
    gc = gspread.service_account(filename="webcambot-ad6a9a73eef6.json")
    # remove to .env
    sh = gc.open(main_file)
    worksheet = sh.sheet1
    result = worksheet.get_all_records(expected_headers=())
    return result
