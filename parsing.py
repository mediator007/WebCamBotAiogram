from functools import lru_cache, wraps
from datetime import datetime, timedelta
import gspread
import schedule
import time


def timed_lru_cache(seconds: int, maxsize: int = 128): 
    def wrapper_cache(func):
        func = lru_cache(maxsize = maxsize)(func)
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

@timed_lru_cache(60) #копирнул с инета, особо в ней не разбирался

def parsing_ID():
    gc = gspread.service_account(filename = "/home/pi/Desktop/Python/WebCamBot_1.1/WebCamBotAiogram/webcambot-ad6a9a73eef6.json") ####C:/Users/User/Desktop/Bot/WebCamBot_1.1/WebCamBot/webcambot-ad6a9a73eef6.json  ####/home/pi/Desktop/Python/WebCamBot_1.1/WebCamBotAiogram/
    sh = gc.open('WebCamBot') ##документ на гугл драйве c айдишниками
    worksheet = sh.sheet1
    result = worksheet.get_all_records() # массив после парсинга документа
    return result

@timed_lru_cache(60)
def parsing_DOC(): # нужно потестить, вероятно будет сбоить во время внесения изменений, особенно кривых
    gc = gspread.service_account(filename = "/home/pi/Desktop/Python/WebCamBot_1.1/WebCamBotAiogram/webcambot-ad6a9a73eef6.json") ####C:/Users/User/Desktop/Bot/WebCamBot_1.1/WebCamBot/webcambot-ad6a9a73eef6.json  ####/home/pi/Desktop/Python/WebCamBot/
    sh = gc.open('КД 2020 Загородный') ##документ на гугл драйве с бухгалтерией
    worksheet = sh.sheet1
    result = worksheet.get_all_records() # массив после парсинга документа
    return result

# if __name__ == '__main__':
#     schedule.every(300).seconds.do(parsing_ID)
#     schedule.every(300).seconds.do(parsing_DOC)
#     schedule.run_pending() 
#     time.sleep(100)