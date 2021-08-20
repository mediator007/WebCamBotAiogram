import sqlite3
import time
import functions as func
import telebot
import config1
import schedule
import parsing as par


WebCamBot = telebot.TeleBot(config1.token)

bonus_table = {
    300:51, 350:52, 400:53, 450:54, 500:55,\
    550:56, 600:57, 650:58, 700:59, 750:60
    }

def spam():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logins")
    datas = cursor.fetchone() # кортеж имен зареганых моделей
    #print(result[2])
    conn.close()
    
    res = par.parsing_DOC()
    result1 = res[-100:]

    if datas != None:
        try:
            for i in range(len(datas)):
                Balance = func.Sum_for_week(result1, datas[i][2]) # если в бд зарегано несколько моделей
                if Balance >= vars.c:
                    WebCamBot.send_message(datas[i][0], text = f"До бонуса 60% осталось всего {750 - Balance}$. Возможно стоит взять еще одну смену!")

        except TypeError:
            Balance = func.Sum_for_week(result1, datas[2]) # если в бд зарегана 1 модель
            print(datas[2])
            print(Balance)
            if Balance >= vars.c:
                    WebCamBot.send_message(datas[0], text = f"До бонуса 60% осталось всего {750 - Balance}$. Возможно стоит взять еще одну смену!")
    else:
        pass

while True:
    schedule.every().day.at("12:00").do(spam)
    schedule.run_pending() 
    time.sleep(30) 

