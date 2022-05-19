import sqlite3
import random
import re

from loguru import  logger
from aiogram import types
from aiogram_calendar import simple_cal_callback, SimpleCalendar
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup

from utils.db_requests import (
    name_by_chat_id,
    name_by_input_id,
    update_chat_id_in_registration,
    delete_from_registration,
    delete_admin_from_db,
    cur_date_report_for_admin,
    date_report_for_admin,
    get_model_list,
    check_id,
    add_model,
    model_name_list,
    delete_model,
    )
from utils.local_vars import (
    available_admin_buttons, 
    )
from utils.functions import OrderDeals
from utils.settings import dp, bot
from utils.messages import create_message_answer

start_kb = ReplyKeyboardMarkup(resize_keyboard=True,)

async def admin_deals(message: types.Message, state):
    """
    Функция обработки комманд от администратора
    """
    if message.text.lower() not in available_admin_buttons:
        await message.answer("Пожалуйста, выберите команду, используя клавиатуру ниже")
        return
    
    # Отчет за текущий день
    elif message.text.lower() == available_admin_buttons[0]:
        cur_date_report = cur_date_report_for_admin()
        if cur_date_report:
            for report in cur_date_report:
                message_answer = create_message_answer(report)
                await message.answer(f"{message_answer}")
        else:
            await message.answer(f"Нет отчетов за сегодня")
        await OrderDeals.waiting_for_admindeals.set()

    # Отчет за выбранную дату
    elif message.text.lower() == available_admin_buttons[1]:
        await message.answer("Выберите дату", reply_markup=await SimpleCalendar().start_calendar())
        await OrderDeals.waiting_for_date.set()
    
    # Список моделей
    elif message.text.lower() == available_admin_buttons[2]:
        models_list = get_model_list()
        if models_list:
            for model in models_list:
                await message.answer(f"Name: {model[0]}  id: {model[1]}")
        else:
            await message.answer(f"Нет зарегестрированных моделей")
        await OrderDeals.waiting_for_admindeals.set()

    # Добавить модель
    elif message.text.lower() == available_admin_buttons[3]:
        await message.answer(f"Добавление модели")
        await message.answer(f"Введите имя с заглавной буквы")
        await OrderDeals.waiting_for_model_add.set()
    
    # Удалить модель
    elif message.text.lower() == available_admin_buttons[4]:
        await message.answer(f"Удаление модели")
        await message.answer(f"Введите имя с заглавной буквы")
        await OrderDeals.waiting_for_model_delete.set()

    # Выход из учетной записи админа
    elif message.text.lower() == available_admin_buttons[-1]:
        chat_id = message.from_user.id
        delete_admin_from_db(chat_id)
        logger.info(f"администратор {chat_id} log out")
        await message.answer("Введите свой ID")
        await OrderDeals.waiting_for_ID.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=OrderDeals.waiting_for_date)
async def process_simple_calendar(callback_query, callback_data: dict):
    """
    Выбор даты администратором и вывод отчета по ней
    """
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        date = date.strftime("%Y-%m-%d")
        date_report = date_report_for_admin(date)

        # If for selected date reports exist:
        if date_report:
            for report in date_report:
                message_answer = create_message_answer(report)
                await callback_query.message.answer(f"{message_answer}")
                await OrderDeals.waiting_for_admindeals.set()
        else:
            await callback_query.message.answer(f"Нет отчетов от моделей за эту дату") 
            await OrderDeals.waiting_for_admindeals.set()


async def model_add(message: types.Message, state):
    """
    Функция добавления модели
    """
    rand_id = random.randint(111111, 999999)
    id_list_tuples = check_id()
    id_list = []
    for t in id_list_tuples:
        id_list.append(t[0])
    # Получение уникального id
    while rand_id in id_list:
        rand_id = random.randint(111111, 999999)

    name = message.text

    # Проверка уникальности имени
    models_names_list_tuple = model_name_list()
    models_names_list = []
    for t in models_names_list_tuple:
        models_names_list.append(t[0])
    
    if name in models_names_list:
        logger.warning(f"Администратор {message.from_user.id} пытался создать {name} повторно")
        await message.answer(f"Имя уже {name} существует в списке зарегестрированных моделей")
        await OrderDeals.waiting_for_admindeals.set()
    
    # Если имя уникально проверяем корректность его ввода регуляркой
    else:
        if bool(re.match(r"[A-Z]{1}[a-z]{1,15}$", name)) == True:
            add_model(name, rand_id)
            logger.info(f"Администратор {message.from_user.id} добавил модель {name}")
            await message.answer(f"Модель {name} зарегестирована с id: {rand_id}")
            await OrderDeals.waiting_for_admindeals.set()
        else:
            logger.warning(f"Администратор {message.from_user.id} некорректно ввел имя {name}")
            await message.answer(f"Введите корректное имя (латиницей, с заглавной буквы, не более 15 символов)")
            await message.answer(f"Например: Maria")
            await OrderDeals.waiting_for_model_add.set()
    

async def model_delete(message: types.Message, state):
    """
    Удаление модели
    """
    models_names_list_tuple = model_name_list()
    models_names_list = []
    for t in models_names_list_tuple:
        models_names_list.append(t[0])

    if message.text in models_names_list:
        delete_model(message.text)
        logger.info(f"Администратор {message.from_user.id} удалил модель {message.text}")
        await message.answer(f"Модель {message.text} удалена")
        await OrderDeals.waiting_for_admindeals.set()
    else:
        await message.answer(f"Модели с таким именем нет")
        await OrderDeals.waiting_for_admindeals.set()