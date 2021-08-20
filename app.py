import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.bot_command import BotCommand
import sqlite3
import config1
import parsing as par
import functions as func
import texts

available_work_buttons = ["узнать баланс", "остаток до бонуса", "выйти из аккаунта"]
available_admin_buttons = ["список моделей", "удалить модель", "выйти из аккаунта"]

conn = sqlite3.connect("database.db") #, check_same_thread = False) # игнор потоков может вызвать коллизию
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS logins (chat_id, ID, Name)""") #Вид бд:  [(383314704, 123123, 'Marzia'), (383314704, 123124, 'Emma')]
conn.commit()
cursor.execute("SELECT * FROM logins")
conn.close()

class OrderDeals(StatesGroup):
    waiting_for_ID = State()
    waiting_for_admindeals = State()
    waiting_for_modeldeals = State()
    waiting_for_modeldelete = State()

async def bot_start(message: types.Message):
    #global Name 
    RegistrationNum = message.from_user.id

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM logins WHERE chat_id = ?", (RegistrationNum, ))
    result = cursor.fetchone()
    conn.close()

    if result: #если есть в бд
        #Name = result[0]
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        for name in available_work_buttons:
            markup.add(name) 
        await message.answer("Сессия восстановлена.", reply_markup=markup)  
        await OrderDeals.waiting_for_modeldeals.set() 
    else: # если нет в бд
        await message.answer(texts.Hello, reply_markup=types.ReplyKeyboardRemove())
        await OrderDeals.waiting_for_ID.set()

async def identification(message: types.Message, state: FSMContext):
    #global Name
    res = par.parsing_ID() 
    try:
        ID = message.text
        if not ID.isdigit():
            await message.answer("Id должен быть числом")
            await OrderDeals.waiting_for_ID.set()
            return # Я не понимаю нахер он нужен
        Num = int(ID)
        search = func.search_id(res,Num) ## Поиск айдишника по массиву
        
        if search == False: ##Если нет айдишника в списке моделей, проверка на айдишник админа
            admin_search = func.admin_search(Num)
            if admin_search == True: # Если айдишник админа - добавляем кнопки, улетаем в функцию админа
                markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
                for name in available_admin_buttons:
                    markup.add(name)
                await message.answer("Сессия администратора", reply_markup=markup)
                await OrderDeals.waiting_for_admindeals.set()

            else: ## Если не модель и не админ - повторяем ввод айдишника
                await message.answer("ID не обнаруже. Попробуйте снова.")
                await OrderDeals.waiting_for_admindeals.set()
        else:
            Name = func.search_name(res, Num)
            RegistrationNum = message.from_user.id
            
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO logins VALUES (?, ?, ?)""", (RegistrationNum, Num, Name))  #заполняем бд для авторизации при ребуте
            conn.commit()
            conn.close()

            markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
            for name in available_work_buttons:
                markup.add(name) 
            await message.answer("Привет "  + Name + ", ты зарегестрирована.", reply_markup=markup)
            await OrderDeals.waiting_for_modeldeals.set()
    except:
        pass 

async def model_deals(message: types.Message, state: FSMContext):
    res = par.parsing_DOC() # парсинг из кэша
    result = res[-100:] # недельный баланс обычно помещается в последнюю сотню строк выдачи
    #print(message.text.lower())
    m = message.from_user.id

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM logins WHERE chat_id = ?", (m, ))
    name = cursor.fetchone()
    conn.close()

    Name = name[0]
    try:
        if message.text.lower() not in available_work_buttons:
            await message.answer("Пожалуйста, выберите команду, используя клавиатуру ниже.")
            return

        if message.text.lower() == available_work_buttons[0]:
            Balance = func.Sum_for_week(result, Name)
            await message.answer(f"Ваш текущий баланс {Balance} $")
            return

        elif message.text.lower() == available_work_buttons[1]:
            Balance = func.Sum_for_week(result, Name)
            await message.answer(func.bonus(Balance))
            return
        
        elif message.text.lower() == available_work_buttons[2]: 
            
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM logins WHERE Name = ?", (Name, ))
            conn.commit()
            conn.close()

            await message.answer("Введите свой ID")
            await OrderDeals.waiting_for_ID.set()
        
    except Exception as e:
        print(e)
        await message.answer(message.chat.id, 'Somthing gone wrong. Try again.')

async def admin_deals(message: types.Message, state: FSMContext):
    if message.text.lower() == available_admin_buttons[0]:
        await message.answer("Список зарегестрированных моделей:") 

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM logins")
        result = cursor.fetchone()
        conn.close()

        if result != None:
            await message.answer(result[0])
            await OrderDeals.waiting_for_admindeals.set()
        else:
            await message.answer('Нет зарегестрированных моделей') #start / stop spam
            await OrderDeals.waiting_for_admindeals.set()
    elif message.text.lower() == available_admin_buttons[1]:
        await message.answer("Введите имя")
        await OrderDeals.waiting_for_modeldelete.set()

    elif message.text.lower() == available_admin_buttons[2]:
        await message.answer("Введите свой ID")
        await OrderDeals.waiting_for_ID.set()

async def model_delete(message: types.Message, state: FSMContext): ## в разработке
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM logins")
    datas = cursor.fetchone()
    #print(message.text.lower())
    #print(datas[0].casefold())
    #conn.close()

    if datas != None:
        try:
            print(1)
            for i in range(len(datas)):
                if datas[i][0].casefold() == message.text.lower():
                    print(2)
                    namefordel = datas[i][0]
                    cursor.execute("DELETE FROM logins WHERE Name = ?", (namefordel, ))
                    await message.answer(texts.DeleteModel)
                    break
        except TypeError:
            print(3)
            if datas[0].casefold() == message.text.lower():
                print(4)
                namefordel = datas[0]
                cursor.execute("DELETE FROM logins WHERE Name = ?", (namefordel, ))
                await message.answer(texts.DeleteModel)
    else:
        await message.answer("Нет зарегестрированных моделей")
    
    conn.commit()
    conn.close()
    await OrderDeals.waiting_for_admindeals.set()

async def bot_help(message: types.Message, state: FSMContext):
    #await state.finish()
    await message.answer(texts.Help)

async def bonus_syst(message: types.Message, state: FSMContext):
    await message.answer(texts.Bonus_table)

async def mailing(message: types.Message, state: FSMContext):
    await message.answer("Раздел находится в разработке")

def register_handlers_deals(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands="start", state="*")
    dp.register_message_handler(bot_help, commands="help", state="*")
    dp.register_message_handler(bonus_syst, commands="bonussyst", state="*")
    dp.register_message_handler(mailing, commands="mailing", state="*")
    dp.register_message_handler(identification, state=OrderDeals.waiting_for_ID)
    dp.register_message_handler(model_deals, state=OrderDeals.waiting_for_modeldeals)
    dp.register_message_handler(admin_deals, state=OrderDeals.waiting_for_admindeals)
    dp.register_message_handler(model_delete, state=OrderDeals.waiting_for_modeldelete)
    

############################################
############################################
############################################

logger = logging.getLogger(__name__)

# Регистрация команд, отображаемых в интерфейсе Telegram
async def set_commands_model(bot: Bot):
    commands = [
        BotCommand(command="/help", description="Помощь"),
        BotCommand(command="/bonussyst", description="Система бонусов"),
        BotCommand(command="/mailing", description="Рассылка"),
        BotCommand(command="/start", description="Перезапуск")
        ]
    await bot.set_my_commands(commands)

async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    bot = Bot(token=config1.token)
    dp = Dispatcher(bot, storage=MemoryStorage())
    # Регистрация хэндлеров
    #register_handlers_common(dp)
    #register_handlers_drinks(dp)
    register_handlers_deals(dp)
    await set_commands_model(bot)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())