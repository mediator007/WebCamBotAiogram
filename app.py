import asyncio
import sqlite3
from typing import List

from aiogram import Bot
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.bot_command import BotCommand
from loguru import logger

from utils.config import token
from utils.parsing import parsing_id, parsing_doc
from utils.functions import search_id, search_name, admin_search, sum_for_week, bonus
from utils import messages as texts
from utils.local_vars import available_work_buttons, available_admin_buttons
from utils.db_requests import is_chat_id_exist, is_input_id_relevant


class OrderDeals(StatesGroup):
    waiting_for_ID = State()
    waiting_for_admindeals = State()
    waiting_for_modeldeals = State()
    waiting_for_modeldelete = State()


async def bot_start(message: types.Message):
    chat_id = message.from_user.id

    # Проверка на наличие chat_id в бд для реконнекта
    with sqlite3.connect("database.db") as conn:
        result = is_chat_id_exist(conn, chat_id)

    # если есть в бд - восстанавливаем сессию
    if result:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in available_work_buttons:
            markup.add(name)
        await message.answer("Сессия восстановлена.", reply_markup=markup)
        logger.info(f"Сессия восстановлена для id {chat_id}")
        await OrderDeals.waiting_for_modeldeals.set()
    # если нет в бд ожидаем ввод id
    else:
        await message.answer(texts.Hello, reply_markup=types.ReplyKeyboardRemove())
        await OrderDeals.waiting_for_ID.set()


async def identification(message: types.Message, state: FSMContext):

    try:
        # введенный id
        input_id = message.text

        if not input_id.isdigit():
            await message.answer("Id должен быть числом")
            await OrderDeals.waiting_for_ID.set()

        input_id = int(input_id)

        # Поиск введенного id  зарегестрированных в бд
        with sqlite3.connect("database.db") as conn:
            validation_result = is_input_id_relevant(conn, input_id)

        # Если нет айдишника в списке моделей, проверка на айдишник админа
        if not validation_result:
            admin_search_res = admin_search(input_id)

            # Если айдишник админа - добавляем кнопки, улетаем в функцию админа
            if admin_search_res:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for name in available_admin_buttons:
                    markup.add(name)
                logger.info(f"Начата сессия администратора")
                await message.answer("Сессия администратора", reply_markup=markup)
                await OrderDeals.waiting_for_admindeals.set()
            
            # Если не модель и не админ - повторяем ввод айдишника
            else:
                logger.warning(f"Неверный ввод id - {input_id}")
                await message.answer("ID не обнаружен. Попробуйте снова.")
                await OrderDeals.waiting_for_ID.set()
        
        # Введенный id найден в файле регистрации
        else:
            # !!!!!Получаем имя модели по введенному id
            name = validation_result[0]
            # id диалога
            chat_id = message.from_user.id

            # !!!!!!!!!! заполняем бд для авторизации при ребуте (id беседы, id модели, имя модели)
            
            # with sqlite3.connect("database.db") as conn:
            #     cursor = conn.cursor()
            #     cursor.execute("""INSERT INTO logins VALUES (?, ?, ?)""",
            #                    (chat_id, num, name))
            #     conn.commit()

            # Добавляем клавиатуру с кнопками из списка
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for button in available_work_buttons:
                markup.add(button)
            logger.info(f"{name} log in")
            await message.answer(f"Привет {name}, ты зарегистрирована.", reply_markup=markup)
            await OrderDeals.waiting_for_modeldeals.set()

    except Exception as e:
        logger.error(f"Ошибка ввода id - {e}")
        await message.answer(texts.Hello, reply_markup=types.ReplyKeyboardRemove())
        await OrderDeals.waiting_for_ID.set()


async def model_deals(message: types.Message, state: FSMContext):
    # парсинг из кэша
    res = parsing_doc()
    # недельный баланс обычно помещается в последнюю сотню строк выдачи
    result = res[-100:]

    dialog_id = message.from_user.id

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM logins WHERE chat_id = ?", (dialog_id,))
        name = cursor.fetchone()

    try:
        Name = name[0]
        if message.text.lower() not in available_work_buttons:
            await message.answer("Пожалуйста, выберите команду, используя клавиатуру ниже.")
            return

        if message.text.lower() == available_work_buttons[0]:
            Balance = sum_for_week(result, Name)
            await message.answer(f"Ваш текущий баланс {Balance:.2f} $")
            return

        elif message.text.lower() == available_work_buttons[1]:
            Balance = sum_for_week(result, Name)
            await message.answer(bonus(Balance))
            return

        elif message.text.lower() == available_work_buttons[2]:

            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM logins WHERE Name = ?", (Name,))
            conn.commit()
            conn.close()
            logger.info(f"{Name} log out")
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

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM logins")
            result = cursor.fetchall()

        try:
            if result[0] is not None:
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
    if datas is not None:
        try:
            for i in range(len(datas)):
                if datas[i][0].casefold() == message.text.lower():  # если много
                    namefordel = datas[i][0]
                    cursor.execute("DELETE FROM logins WHERE Name = ?", (namefordel,))
                    await message.answer(texts.DeleteModel)
                    break
                else:
                    await message.answer("Имя не обнаружено")

        except TypeError as e:
            logger.error(f"Model delete with with {e}")
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
    bot = Bot(token=token)
    dp = Dispatcher(bot, storage=MemoryStorage())
    register_handlers_deals(dp)
    await set_commands_model(bot)
    await dp.start_polling()


if __name__ == '__main__':
    logger.add("bot_debug.log", format="{time} {level} {message}", level="INFO", rotation="1 MB")
    logger.info("Bot start")
    asyncio.run(main())
