import telebot
from telebot import types #директория types в библиотеке telebot для кнопок
import config1 #токен
#from google.oauth2 import service_account
#from gspread.models import Worksheet
import functions as func
import sqlite3
import parsing as par 

conn = sqlite3.connect("database.db") #, check_same_thread = False) # игнор потоков может вызвать коллизию
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS logins (chat_id, ID, Name)""") #Вид бд:  [(383314704, 123123, 'Marzia'), (383314704, 123124, 'Emma')]
conn.commit()
cursor.execute("SELECT * FROM logins")
conn.close()

WebCamBot = telebot.TeleBot(config1.token)

@WebCamBot.message_handler(content_types = 'text')

#проверка по базе данных. Если айди_чата есть в БД возобновляем функцию def Work(message) подтягивая айдишник через ИМЯ и документ WebCamBot.exe

def send_welcome(message):
    global Name #Это пздц, у меня тут одна глобалка объявляется в 2х разных функциях. Возможно это катастрофа
    RegistrationNum = message.from_user.id
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM logins WHERE chat_id = ?", (RegistrationNum, ))
    result = cursor.fetchone()
    conn.close()

    if result:
        Name = result[0] 
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        Balance = types.KeyboardButton(text = 'Week Balance')
        markup.add(Balance) 
        Bonus = types.KeyboardButton(text = 'Bonus') 
        markup.add(Bonus) 
        Balance = types.KeyboardButton(text = 'Log Out')
        markup.add(Balance)
        msg = WebCamBot.send_message(message.chat.id, text = """Back session""", reply_markup = markup) ## reply нужен для кнопок!
        WebCamBot.register_next_step_handler(msg, Work)
    else:
        msg = WebCamBot.reply_to(message, """Hi there, I am WebCam bot. Enter your ID!""")
        WebCamBot.register_next_step_handler(msg, IDidentification)
    
def IDidentification(message):
    global Name # опять эта хуйня. Как бы от неё избавиться
    res = par.parsing_ID() 
    try:
        ID = message.text
        if not ID.isdigit():
            msg = WebCamBot.reply_to(message, 'ID should be a number. Enter your ID')
            WebCamBot.register_next_step_handler(msg, IDidentification)
            return # Я не понимаю нахер он нужен
        Num = int(ID)
        search = func.search_id(res,Num) ## Поиск айдишника по массиву
        if search == False: ##Если нет айдишника в списке моделей, проверка на айдишник админа
            admin_search = func.admin_search(Num)
            if admin_search == True: # Если айдишник админа - добавляем кнопки, улетаем в функцию админа
                markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                Admin1 = types.KeyboardButton(text = 'Models list')
                markup.add(Admin1) 
                Admin2 = types.KeyboardButton(text = 'Delete model') 
                markup.add(Admin2)
                Admin3 = types.KeyboardButton(text = 'Log Out') 
                markup.add(Admin3) 
                msg = WebCamBot.send_message(message.chat.id, "Admin session.Choose admin deals", reply_markup = markup)
                WebCamBot.register_next_step_handler(msg, Administration)
            else: ## Если не модель и не админ - повторяем ввод айдишника
                msg = WebCamBot.reply_to(message, 'No such ID. Try again.')
                WebCamBot.register_next_step_handler(msg, IDidentification)
                #return
        else:
            Name = func.search_name(res, Num)
            RegistrationNum = message.from_user.id
            #Registration[RegistrationNum] = Name #Каждый новый пользователь забивает в словарь имя с ключем chat.id

            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO logins VALUES (?, ?, ?)""", (RegistrationNum, Num, Name))  #заполняем бд для авторизации при ребуте
            conn.commit()
            #cursor.execute("SELECT * FROM logins")
            #print(cursor.fetchall())
            conn.close()

            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            Balance = types.KeyboardButton(text = 'Week Balance')
            markup.add(Balance) 
            Bonus = types.KeyboardButton(text = 'Bonus') 
            markup.add(Bonus)
            Bonus = types.KeyboardButton(text = 'Log Out') 
            markup.add(Bonus) 

            msg = WebCamBot.send_message(message.chat.id, text = "Congratulations "  + Name + ", you are registered now.", reply_markup = markup)
            WebCamBot.register_next_step_handler(msg, Work)
    except Exception as e:
        print(e)
        WebCamBot.reply_to(message, 'Somthing gone wrong. Try again.')
        #WebCamBot.register_next_step_handler(msg, send_welcome)

def Work(message):
    res = par.parsing_DOC() # парсинг из кэша
    result = res[-100:] # недельный баланс обычно помещается в последнюю сотню строк выдачи
    try:
        Input = message.text
        if Input == 'Week Balance':
            Balance = func.Sum_for_week(result, Name)
            msg = WebCamBot.send_message(message.chat.id, Balance)
            WebCamBot.register_next_step_handler(msg, Work)
        elif Input == 'Bonus':
            msg = WebCamBot.send_message(message.chat.id, 'BONUS') # Пустая кнопка. Пока не прикрутил к ней запрос остатка до бонуса
            WebCamBot.register_next_step_handler(msg, Work)
        elif Input == 'Log Out': 
            
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM logins WHERE Name = ?", (Name, ))
            conn.commit()
            conn.close()

            msg = WebCamBot.send_message(message.chat.id, 'You Log Out')
            WebCamBot.register_next_step_handler(msg, send_welcome)
        else:
            msg = WebCamBot.send_message(message.chat.id, 'Unknown command')
            WebCamBot.register_next_step_handler(msg, Work)
    except:
        WebCamBot.reply_to(message, 'Somthing gone wrong. Try again.')

def Administration(message):
    Input = message.text
    if Input == 'Models list':
        WebCamBot.send_message(message.chat.id, 'Registered models:') 

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM logins")
        result = cursor.fetchone()
        conn.close()
        if result != None:
            msg = WebCamBot.send_message(message.chat.id, result) 
            WebCamBot.register_next_step_handler(msg, Administration)
        else:
            msg = WebCamBot.send_message(message.chat.id, 'No registered models') #start / stop spam
            WebCamBot.register_next_step_handler(msg, Administration)
    
    elif Input == 'Delete model':
        msg = WebCamBot.send_message(message.chat.id, 'Enter name') 
        WebCamBot.register_next_step_handler(message = msg, callback = Delete_model)
    
    elif Input == 'Start / Stop Spam':
        msg = WebCamBot.send_message(message.chat.id, 'Stop spam') #start / stop spam еще не готово
        WebCamBot.register_next_step_handler(msg, Administration)
    
    elif Input == 'Log Out':
        msg = WebCamBot.send_message(message.chat.id, 'Log Out')
        WebCamBot.register_next_step_handler(msg, send_welcome)
    
    else:
        msg = WebCamBot.send_message(message.chat.id, 'Unknown command')
        WebCamBot.register_next_step_handler(msg, Administration)

def Delete_model(message): #### При удалении модели проверять её актуальность в бд 
    Input = message.text
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logins")
    result = cursor.fetchone()
    conn.close()
    if result != None:
        try:
            for i in range(len(result)):
                if Input == result[i][2]:
                    namefordel = result[i][2]
                    conn = sqlite3.connect("database.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM logins WHERE Name = ?", (namefordel, ))
                    conn.commit()
                    conn.close()
                    msg = WebCamBot.send_message(message.chat.id, 'Model delete')
                    WebCamBot.register_next_step_handler(msg, Administration)
                else:
                    msg = WebCamBot.send_message(message.chat.id, 'No such model')
                    WebCamBot.register_next_step_handler(msg, Administration)
        
        except TypeError:
            if Input == result[2]:
                namefordel = result[2]
                conn = sqlite3.connect("database.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM logins WHERE Name = ?", (namefordel, ))
                conn.commit()
                conn.close()
                msg = WebCamBot.send_message(message.chat.id, 'Model delete')
                WebCamBot.register_next_step_handler(msg, Administration)
            else:
                msg = WebCamBot.send_message(message.chat.id, 'No such model')
                WebCamBot.register_next_step_handler(msg, Administration)
    else:
        msg = WebCamBot.send_message(message.chat.id, 'No registered models')
        WebCamBot.register_next_step_handler(msg, Administration)


WebCamBot.polling(none_stop = True)
WebCamBot.infinity_polling()