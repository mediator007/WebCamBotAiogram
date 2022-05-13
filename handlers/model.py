import sqlite3
from loguru import  logger

from utils.db_requests import (
    name_by_chat_id,
    name_by_input_id,
    update_chat_id_in_registration,
    delete_from_registration,
)
from utils.local_vars import available_work_buttons, available_admin_buttons
from utils.functions import OrderDeals

async def model_deals(message):
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