import sqlite3
import time
import functions as func
import telebot
import config1
import schedule
import parsing as par
#import asyncio


WebCamBot = telebot.TeleBot(config1.token)

bonus_table = {
    300:51, 350:52, 400:53, 450:54, 500:55,\
    550:56, 600:57, 650:58, 700:59, 750:60
    }

def spam():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logins")
    datas = cursor.fetchall() # кортеж имен зареганых моделей
    print(datas)
    conn.close()
    
    res = par.parsing_DOC()
    result1 = res[-100:]

    if datas != None:
        Balance = func.Sum_for_week(result1, datas[2]) # если в бд зарегана 1 модель
        if Balance >= vars.c:
            WebCamBot.send_message(datas[0], text = f"До бонуса 60% осталось всего {750 - Balance}$. Возможно стоит взять еще одну смену!")
        else:
            for i in range(len(datas)):
                Balance = func.Sum_for_week(result1, datas[i][2]) # если в бд зарегано несколько моделей
                if Balance >= vars.c:
                    WebCamBot.send_message(datas[i][0], text = f"До бонуса 60% осталось всего {750 - Balance}$. Возможно стоит взять еще одну смену!")
    else:
        print("NO models for spam")
        pass

while True:
    schedule.every(0.25).minutes.do(spam)
    #schedule.every().day.at("12:00").do(spam)
    schedule.run_pending() 
    #asyncio.sleep(30) 

