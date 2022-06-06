# V2
import sqlite3
from unicodedata import digit
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
    rows_for_week,
    get_admin_list,
    )

from utils.local_vars import (
    available_sites_buttons,
    available_work_buttons,
    )

from utils.functions import (
    OrderDeals, 
    sum_for_week, 
    bonus, 
    for_next_bonus,
    create_keyboard,
    sites_cb,
    get_keyboard,
    )
from utils.settings import dp, bot

current_date = date.today()

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
            logger.info(f"{name} отправление отчета")
            await message.answer(f"Выберите сайт", reply_markup=get_keyboard())
            await OrderDeals.waiting_for_report.set()

        # Если нажато Узнать баланс
        if message.text.lower() == available_work_buttons[1]:
            logger.info(f"{name} запрос баланса")
            with sqlite3.connect("database.db") as conn:
                rows = rows_for_week(conn, name)
            
            week_result = sum_for_week(rows)
            week_bonus = bonus(week_result)
            model_get = week_result * (week_bonus / 100)

            await message.answer(
                f"Ваш текущий баланс {model_get:.2f} $ \n"
                f"Ваш бонус {week_bonus} %"
                )
            return

        # Если нажато Остаток до бонуса
        elif message.text.lower() == available_work_buttons[2]:
            logger.info(f"{name} запрос остатка до бонуса")
            with sqlite3.connect("database.db") as conn:
                rows = rows_for_week(conn, name)

            week_result = sum_for_week(rows)
            if week_result >= 750:
                await message.answer(f"У вас максимальный бонус 60 %")
                return
            else:
                week_bonus = bonus(week_result)
                remains = for_next_bonus(week_result)
                await message.answer(f"До следующего бонуса в {week_bonus + 1}% осталось {remains:.2f}$")
                return

        # Если нажато Выйти из аккаунта
        elif message.text.lower() == available_work_buttons[3]:

            # Удаляем chat_id из registration
            with sqlite3.connect("database.db") as conn:
                delete_from_registration(conn, chat_id)

            logger.info(f"{name} log out")
            await message.answer("Введите свой ID")
            await OrderDeals.waiting_for_ID.set()

    except Exception as e:
        logger.error(f"Ошибка в model_deals: {e}")
        await message.answer('Возникли проблемы. Попробуйте перезапустить бот.')
        await message.answer("Введите свой ID")
        await OrderDeals.waiting_for_ID.set()


@dp.callback_query_handler(sites_cb.filter(action=[
    available_sites_buttons[0], 
    available_sites_buttons[1],
    available_sites_buttons[2],
    available_sites_buttons[3],
    available_sites_buttons[4],
    available_sites_buttons[5],
    available_sites_buttons[6]
    ]), state=OrderDeals.waiting_for_report)
async def report_by_site(callback_query, state):
    """
    Функция принимает сайт для записи суммы
    """
    answer_data = callback_query.data[5:]
    logger.info(f"Для отчета выбран {answer_data}")
    await state.update_data(chosen_site=answer_data.lower())
    
    if answer_data in (
        available_sites_buttons[0], 
        available_sites_buttons[1],
        available_sites_buttons[4],
        available_sites_buttons[5],
        available_sites_buttons[6],
    ):
        await bot.send_message(
            callback_query.from_user.id, f"Введите сумму в токенах для {answer_data}", 
            reply_markup= types.ReplyKeyboardRemove()
        )

    elif answer_data in (
        available_sites_buttons[2], 
        available_sites_buttons[3],
    ):
        await bot.send_message(
            callback_query.from_user.id, f"Введите сумму в долларах для {answer_data}", 
            reply_markup= types.ReplyKeyboardRemove()
        )

    await OrderDeals.waiting_for_report_sum.set()


@dp.message_handler(state=OrderDeals.waiting_for_report_sum)
async def report_sum(message, state):
    """
    Функция принимает сумму для записи в бд
    """

    markup = create_keyboard(available_work_buttons)

    report_sum = message.text
    if not report_sum.isdigit():
        logger.warning(f"Report input not is digit: {report_sum}")
        await message.answer("Сумма должна быть числом", reply_markup=markup)
        await OrderDeals.waiting_for_modeldeals.set()
        return

    chat_id = message.from_user.id
    try:
        report_sum = int(message.text)
        site = await state.get_data()
        site = site['chosen_site']

        # Запись суммы в БД
        with sqlite3.connect("database.db") as conn:
            name = name_by_chat_id(conn, chat_id)
            name = name[0]
            add_report(conn, current_date, name, site, report_sum)

        # Дублирование отчета админам из БД
        admin_list = get_admin_list()
        for admin in admin_list:
            logger.info(f"Отчет отправлен админу {admin[0]}")
            await bot.send_message(admin[0], f"{name} - {site} - {report_sum}")

        logger.info(f"{name} занесение в БД {report_sum} в {site} ")
        await message.answer(f"В {site} записано {report_sum}", reply_markup=markup)
        await OrderDeals.waiting_for_modeldeals.set()
    
    except Exception as e:
        logger.error(f"Ошибка ввода суммы: {e}")
        await message.answer("Сумма должна быть целым числом", reply_markup=markup)
        await OrderDeals.waiting_for_modeldeals.set()