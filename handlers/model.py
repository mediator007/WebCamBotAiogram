import sqlite3
from loguru import  logger
from aiogram import types
from aiogram.utils.callback_data import CallbackData
from datetime import date

from utils.db_requests import (
    name_by_chat_id,
    name_by_input_id,
    update_chat_id_in_registration,
    delete_from_registration,
    add_report,
    )

from utils.local_vars import (
    available_work_buttons, 
    available_sites_buttons,
    )

from utils.functions import OrderDeals
from utils.settings import dp, bot

current_date = date.today()
# print(current_date)

sites_cb = CallbackData('vote', 'action')  # vote:<action>

def get_keyboard():
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1)
    row_btns_1 = (
        types.InlineKeyboardButton(available_sites_buttons[0], callback_data=sites_cb.new(action=available_sites_buttons[0])),
        types.InlineKeyboardButton(available_sites_buttons[1], callback_data=sites_cb.new(action=available_sites_buttons[1])),
        types.InlineKeyboardButton(available_sites_buttons[2], callback_data=sites_cb.new(action=available_sites_buttons[2])),
        )
    row_btns_2 = (
        types.InlineKeyboardButton(available_sites_buttons[3], callback_data=sites_cb.new(action=available_sites_buttons[3])),
        types.InlineKeyboardButton(available_sites_buttons[4], callback_data=sites_cb.new(action=available_sites_buttons[4])),
        types.InlineKeyboardButton(available_sites_buttons[5], callback_data=sites_cb.new(action=available_sites_buttons[5])),
        )
    keyboard_markup.row(*row_btns_1)
    keyboard_markup.row(*row_btns_2)
    return keyboard_markup

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
            
            await message.answer(f"Выберите сайт", reply_markup=get_keyboard())
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


@dp.callback_query_handler(sites_cb.filter(action=[
    available_sites_buttons[0], 
    available_sites_buttons[1],
    available_sites_buttons[2],
    available_sites_buttons[3],
    available_sites_buttons[4],
    available_sites_buttons[5]
    ]), state=OrderDeals.waiting_for_report)
async def report_by_site(callback_query, state):
    """
    Функция принимает сайт для записи суммы
    """

    answer_data = callback_query.data[5:]
    await state.update_data(chosen_site=answer_data.lower())
    await callback_query.answer(f'Введите сумму для {answer_data}')
    await OrderDeals.waiting_for_report_sum.set()

@dp.message_handler(state=OrderDeals.waiting_for_report_sum)
async def report_sum(message, state):
    """
    Функция принимает сумму для записи в бд
    """
    report_sum = message.text
    chat_id = message.from_user.id
    try:
        report_sum = int(message.text)
        site = await state.get_data()
        site = site['chosen_site']

        with sqlite3.connect("database.db") as conn:
            name = name_by_chat_id(conn, chat_id)

            name = name[0]
            add_report(conn, current_date, name, site, report_sum)

        await message.answer(f"В {site} записано {report_sum}")
        await OrderDeals.waiting_for_modeldeals.set() 
    
    except Exception as e:
        logger.error(f"Ошибка ввода суммы: {e}")
        await message.answer("Сумма должна быть числом")
        await OrderDeals.waiting_for_modeldeals.set()