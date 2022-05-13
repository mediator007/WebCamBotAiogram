import asyncio
import sqlite3
from typing import List

from aiogram import Bot
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup
from aiogram.types.bot_command import BotCommand
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from aiogram.utils.callback_data import CallbackData
from loguru import logger

from utils.config import token
from utils.parsing import parsing_id, parsing_doc
from utils.functions import admin_search, sum_for_week, bonus
from utils import messages as texts
from utils.local_vars import available_work_buttons, available_admin_buttons
from utils.db_requests import (
    name_by_chat_id,
    name_by_input_id,
    update_chat_id_in_registration,
    delete_from_registration,
)

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
start_kb = ReplyKeyboardMarkup(resize_keyboard=True,)


class OrderDeals(StatesGroup):
    waiting_for_ID = State()
    waiting_for_admindeals = State()
    waiting_for_modeldeals = State()
    waiting_for_modeldelete = State()
    waiting_for_date = State()  # Calendar


async def bot_start(message: types.Message):
    """
    Функция первоначального запуска бота или ребута
    """
    chat_id = message.from_user.id

    # Проверка на наличие chat_id в бд для реконнекта
    with sqlite3.connect("database.db") as conn:
        result = name_by_chat_id(conn, chat_id)

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
    """
    Функция валидации введенного id
    """

    try:
        # введенный id
        input_id = message.text

        if not input_id.isdigit():
            await message.answer("Id должен быть числом")
            await OrderDeals.waiting_for_ID.set()

        input_id = int(input_id)

        # Поиск введенного id  зарегестрированных в бд
        with sqlite3.connect("database.db") as conn:
            validation_result = name_by_input_id(conn, input_id)

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

        # Введенный id найден в registration
        else:
            # Получаем имя модели по введенному id
            name = validation_result[0]
            # id диалога
            chat_id = message.from_user.id

            # Обновляем поле chat_id в бд для авторизации при ребуте
            with sqlite3.connect("database.db") as conn:
                update_chat_id_in_registration(conn, chat_id, input_id)

            # Добавляем клавиатуру с кнопками из списка
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for button in available_work_buttons:
                markup.add(button)

            logger.info(f"{name} log in")
            await message.answer(f"Привет {name}, ты зарегистрирована.", reply_markup=markup)
            await OrderDeals.waiting_for_modeldeals.set()

    except Exception as exc:
        logger.error(f"Ошибка ввода id - {exc}")
        await message.answer(texts.Hello, reply_markup=types.ReplyKeyboardRemove())
        await OrderDeals.waiting_for_ID.set()


async def model_deals(message: types.Message, state: FSMContext):
    """
    Функция обработки команд модели 
    (Запрос баланса, остаток до бонуса, выход из аккаунта)
    """

    chat_id = message.from_user.id

    # Получаем имя для поиска результатов по датам и имени в main 
    with sqlite3.connect("database.db") as conn:
        name = name_by_chat_id(conn, chat_id)

    try:
        name = name[0]

        # Если введен текст вместо нажатия кнопки
        if message.text.lower() not in available_work_buttons:
            await message.answer("Пожалуйста, выберите команду, используя клавиатуру ниже.")
            return

        # Если нажато Узнать баланс
        if message.text.lower() == available_work_buttons[0]:

            # balance = sum_for_week(result, name)

            await message.answer(f"Ваш текущий баланс balance $")
            return

        # Если нажато Остаток до бонуса
        elif message.text.lower() == available_work_buttons[1]:

            # balance = sum_for_week(result, name)

            await message.answer("bonus(Balance)")
            return

        # Если нажато Выйти из аккаунта
        elif message.text.lower() == available_work_buttons[2]:

            # Удаляем 
            with sqlite3.connect("database.db") as conn:
                delete_from_registration(conn, chat_id)

            logger.info(f"{name} log out")
            await message.answer("Введите свой ID")
            await OrderDeals.waiting_for_ID.set()

    except TypeError:
        await message.answer('Возникли проблемы. Обратитесь к администратору.')
        await message.answer("Введите свой ID")
        await OrderDeals.waiting_for_ID.set()


async def admin_deals(message: types.Message, state: FSMContext):
    """
    Функция обработки комманд от администратора
    """
    if message.text.lower() not in available_admin_buttons:
        await message.answer("Пожалуйста, выберите команду, используя клавиатуру ниже.")
        return

    elif message.text.lower() == available_admin_buttons[0]:
        await message.answer("Список зарегестрированных моделей:", reply_markup=await SimpleCalendar().start_calendar())
        await OrderDeals.waiting_for_date.set()

    # elif message.text.lower() == available_admin_buttons[1]:
    #     await message.answer("Введите имя")
    #     await OrderDeals.waiting_for_modeldelete.set()
    #
    # elif message.text.lower() == available_admin_buttons[2]:
    #     await message.answer("Введите свой ID")
    #     await OrderDeals.waiting_for_ID.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=OrderDeals.waiting_for_date)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    print(callback_query, callback_data)
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    print(date)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=start_kb
        )


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
    dp.register_message_handler(callback=bot_start, commands="start", state="*")
    dp.register_message_handler(callback=bot_help, commands="help", state="*")
    dp.register_message_handler(callback=bonus_syst, commands="bonussyst", state="*")
    dp.register_message_handler(callback=mailing, commands="mailing", state="*")
    dp.register_message_handler(callback=identification, state=OrderDeals.waiting_for_ID)
    dp.register_message_handler(callback=model_deals, state=OrderDeals.waiting_for_modeldeals)
    dp.register_message_handler(callback=admin_deals, state=OrderDeals.waiting_for_admindeals)
    dp.register_message_handler(callback=model_delete, state=OrderDeals.waiting_for_modeldelete)
    # Calendar
    # dp.register_callback_query_handler(process_dialog_calendar, simple_cal_callback.filter())


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
    register_handlers_deals(dp)
    await set_commands_model(bot)
    await dp.start_polling()


if __name__ == '__main__':
    logger.add("bot_debug.log", format="{time} {level} {message}", level="INFO", rotation="1 MB")
    logger.info("Bot start")
    asyncio.run(main())
