import asyncio
import logging
from aiogram import Bot, Dispatcher, types
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

conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS logins (chat_id, ID, Name)""") 
conn.commit()
cursor.execute("SELECT * FROM logins")
conn.close()

class OrderDeals(StatesGroup):
    waiting_for_ID = State()
    waiting_for_admindeals = State()
    waiting_for_modeldeals = State()
    waiting_for_modeldelete = State()

async def bot_start(message: types.Message):
    RegistrationNum = message.from_user.id

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM logins WHERE chat_id = ?", (RegistrationNum, ))
    result = cursor.fetchone()
    conn.close()

    if result: #если есть в бд
        markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
        for name in available_work_buttons:
            markup.add(name) 
        await message.answer("Сессия восстановлена.", reply_markup=markup)  
        await OrderDeals.waiting_for_modeldeals.set() 
    else: # если нет в бд
        await message.answer(texts.Hello, reply_markup=types.ReplyKeyboardRemove())
        await OrderDeals.waiting_for_ID.set()

async def identification(message: types.Message, state: FSMContext):
    res = par.parsing_ID() 
    try:
        ID = message.text
        if not ID.isdigit():
            await message.answer("Id должен быть числом")
            await OrderDeals.waiting_for_ID.set()
            return 
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
                await message.answer("ID не обнаружен. Попробуйте снова.")
                await OrderDeals.waiting_for_ID.set()
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
    
    m = message.from_user.id

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM logins WHERE chat_id = ?", (m, ))
    name = cursor.fetchone()
    conn.close()
    
    try:
        Name = name[0]
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
        
    except TypeError:
        await message.answer('Возникли проблемы. Обратитесь к администратору.')
        await message.answer("Введите свой ID")
        await OrderDeals.waiting_for_ID.set()


async def admin_deals(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_admin_buttons:
        await message.answer("Пожалуйста, выберите команду, используя клавиатуру ниже.")
        return

    elif message.text.lower() == available_admin_buttons[0]:
        await message.answer("Список зарегестрированных моделей:") 

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM logins")
        result = cursor.fetchall()
        print(result)
        conn.close()

        try:
            if result[0] != None:
                for i in range(len(result)):
                    await message.answer(result[i][0])
                    await OrderDeals.waiting_for_admindeals.set()
        except IndexError:
            await message.answer('Нет зарегестрированных моделей') 
            await OrderDeals.waiting_for_admindeals.set()

    elif message.text.lower() == available_admin_buttons[1]:
        await message.answer("Введите имя")
        await OrderDeals.waiting_for_modeldelete.set()

    elif message.text.lower() == available_admin_buttons[2]:
        await message.answer("Введите свой ID")
        await OrderDeals.waiting_for_ID.set()

async def model_delete(message: types.Message, state: FSMContext):
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM logins")
    datas = cursor.fetchall()
    if datas != None:
        try:
            for i in range(len(datas)):
                if datas[i][0].casefold() == message.text.lower(): # если много
                    namefordel = datas[i][0]
                    cursor.execute("DELETE FROM logins WHERE Name = ?", (namefordel, ))
                    await message.answer(texts.DeleteModel)
                    break
                else:
                    await message.answer("Имя не обнаружено")

        except TypeError as e:
            print(e)
    else:
        await message.answer("Такое имя отсутствует")
    
    conn.commit()
    conn.close()
    await OrderDeals.waiting_for_admindeals.set()

async def bot_help(message: types.Message, state: FSMContext):
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
    register_handlers_deals(dp)
    await set_commands_model(bot)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())