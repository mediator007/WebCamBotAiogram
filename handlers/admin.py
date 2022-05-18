import sqlite3
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
        await message.answer("Пожалуйста, выберите команду, используя клавиатуру ниже.")
        return
    
    # Отчет за текущий день
    elif message.text.lower() == available_admin_buttons[0]:
        cur_date_report = cur_date_report_for_admin()
        for report in cur_date_report:
            message_answer = create_message_answer(report)
            await message.answer(f"{message_answer}")
        await OrderDeals.waiting_for_admindeals.set()

    # Отчет за выбранную дату
    elif message.text.lower() == available_admin_buttons[1]:
        await message.answer("Выберите дату", reply_markup=await SimpleCalendar().start_calendar())
        await OrderDeals.waiting_for_date.set()

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
        # await callback_query.message.answer(
        #     f'You selected {date.strftime("%d/%m/%Y")}',
        #     reply_markup=start_kb
        # )
        # Вывод отчета за выбранную дату
        date = date.strftime("%Y-%m-%d")
        date_report = date_report_for_admin(date)

        # If for selected date reports exist:
        if date_report:
            for report in date_report:
                message_answer = create_message_answer(report)
                await callback_query.message.answer(f"{message_answer}")
                await OrderDeals.waiting_for_admindeals.set()
        else:
            await callback_query.message.answer(f"Нет отчетов от моделей") 
            await OrderDeals.waiting_for_admindeals.set()