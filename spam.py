import sqlite3
import time
import functions as func
import telebot
import config1
import gspread
import schedule
import parsing as par


WebCamBot = telebot.TeleBot(config1.token)

c = 50 # сумма необходимая для бонуса. Пока для примера 50

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
                print(Balance)
                if Balance >= c:
                    msg = WebCamBot.send_message(datas[i][0], text = "Your balance is more then c. Take a shift on this week for bonus")

        except TypeError:
            Balance = func.Sum_for_week(result1, datas[2]) # если в бд зарегана 1 модель
            print(datas[2])
            print(Balance)
            if Balance >= c:
                    msg = WebCamBot.send_message(datas[0], text = "Your balance is more then c. Take a shift on this week for bonus")
    else:
        pass

while True:
    #schedule.every(30).seconds.do(spam)
    schedule.every().day.at("12:00").do(spam)
    schedule.run_pending() # не понял нах это нужно
    time.sleep(30) 

