import sqlite3
import time
import telebot
import schedule
from utils import parsing as par, config, functions as func, local_vars

WebCamBot = telebot.TeleBot(config1.token)

bonus_table = {
    300: 51, 350: 52, 400: 53, 450: 54, 500: 55, \
    550: 56, 600: 57, 650: 58, 700: 59, 750: 60
}


def spam():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logins")
    datas = cursor.fetchall()  # кортеж имен зареганых моделей
    # datas = datas1[-100:]
    print(datas)
    conn.close()

    res = par.parsing_DOC()
    result1 = res[-100:]

    if datas != None:
        for i in range(len(datas)):
            print(len(datas))
            Balance = func.Sum_for_week(result1, datas[i][2])
            if Balance >= local_vars.c:
                WebCamBot.send_message(
                    datas[i][0], text=f"До бонуса 60% осталось всего {750 - Balance}$. "
                                      f"Возможно стоит взять еще одну смену!"
                )

    else:
        print("NO models for spam")
        pass


while True:
    schedule.every(1).hour.do(spam)
    # schedule.every().day.at("12:00").do(spam)
    schedule.run_pending()
    time.sleep(60)
