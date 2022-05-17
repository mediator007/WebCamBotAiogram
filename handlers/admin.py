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
    get_admin_list
    )

from utils.local_vars import (
    available_admin_buttons, 
    )

from utils.functions import OrderDeals
from utils.settings import dp, bot

start_kb = ReplyKeyboardMarkup(resize_keyboard=True,)

async def admin_deals(message: types.Message, state):
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

    elif message.text.lower() == available_admin_buttons[-1]:
        chat_id = message.from_user.id
        delete_admin_from_db(chat_id)
        await message.answer("Введите свой ID")
        await OrderDeals.waiting_for_ID.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=OrderDeals.waiting_for_date)
async def process_simple_calendar(callback_query, callback_data: dict):
    # print(callback_query, callback_data)
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    # print(date)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=start_kb
        )
        await OrderDeals.waiting_for_admindeals.set()