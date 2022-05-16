import sqlite3
from loguru import  logger
from aiogram import types

from utils.db_requests import (
    name_by_chat_id,
    name_by_input_id,
    update_chat_id_in_registration,
    delete_from_registration,
    )

from utils.local_vars import (
    available_work_buttons, 
    available_sites_buttons,
    )

from utils.functions import OrderDeals
from utils.settings import dp, bot

async def model_deals(message):
    """
    Функция обработки команд модели
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

        # Если нажато Отправить отчет
        if message.text.lower() == available_work_buttons[0]:
            
            keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
            row_btns_1 = (types.InlineKeyboardButton(text, callback_data=text) for text in available_sites_buttons[:3])
            row_btns_2 = (types.InlineKeyboardButton(text, callback_data=text) for text in available_sites_buttons[3:])
            keyboard_markup.row(*row_btns_1)
            keyboard_markup.row(*row_btns_2)
            
            await message.answer(f"Выберите сайт", reply_markup=keyboard_markup)
            await OrderDeals.waiting_for_report.set()

        # Если нажато Узнать баланс
        if message.text.lower() == available_work_buttons[1]:

            # balance = sum_for_week(result, name)

            await message.answer(f"Ваш текущий баланс balance $")
            return

        # Если нажато Остаток до бонуса
        elif message.text.lower() == available_work_buttons[2]:

            # balance = sum_for_week(result, name)

            await message.answer("bonus(Balance)")
            return

        # Если нажато Выйти из аккаунта
        elif message.text.lower() == available_work_buttons[3]:

            # Удаляем
            with sqlite3.connect("database.db") as conn:
                delete_from_registration(conn, chat_id)

            logger.info(f"{name} log out")
            await message.answer("Введите свой ID")
            await OrderDeals.waiting_for_ID.set()

    except Exception as e:
        print(e)
        await message.answer('Возникли проблемы. Обратитесь к администратору.')
        await message.answer("Введите свой ID")
        await OrderDeals.waiting_for_ID.set()


@dp.callback_query_handler(text='Jasmin', state=OrderDeals.waiting_for_report)
async def report_by_site(callback_query):

    answer_data = callback_query.data
    await callback_query.answer(f'You answered with {answer_data!r}')
    await OrderDeals.waiting_for_modeldeals.set()