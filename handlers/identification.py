import sqlite3
from aiogram import Dispatcher, types
from loguru import logger

from utils.functions import OrderDeals, create_keyboard
from utils.db_requests import name_by_input_id
from utils.local_vars import available_admin_buttons, available_work_buttons, admin_pass
from utils.db_requests import (
    update_chat_id_in_registration, 
    add_admin_to_db,
    check_model_auth,
    )
from utils import messages as texts


async def identification(message):
    """
    Функция валидации введенного id
    """

    try:
        # введенный id
        input_id = message.text

        if not input_id.isdigit():
            logger.warning(f"id input not is digit: {input_id}")
            await message.answer("Id должен быть числом")
            await OrderDeals.waiting_for_ID.set()
            return

        input_id = int(input_id)

        # Поиск введенного id  зарегестрированных в бд
        with sqlite3.connect("database.db") as conn:
            validation_result = name_by_input_id(conn, input_id)

        # Если нет айдишника в списке моделей, проверка на айдишник админа
        if not validation_result:

            # Если айдишник админа - добавляем кнопки, улетаем в функцию админа
            if input_id == admin_pass:
                chat_id = message.from_user.id
                add_admin_to_db(chat_id)

                markup = create_keyboard(available_admin_buttons)

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

            # Проверка на повторную аутентификацию by model
            check_double_reg = check_model_auth(input_id)
            if check_double_reg[0][0] is not None:
                await message.answer("Данная модель уже зарегестрирована")
                await OrderDeals.waiting_for_ID.set()
            
            else:
                # Получаем имя модели по введенному id
                name = validation_result[0]
                # id диалога
                chat_id = message.from_user.id

                # Обновляем поле chat_id в бд для авторизации при ребуте
                with sqlite3.connect("database.db") as conn:
                    update_chat_id_in_registration(conn, chat_id, input_id)

                # Добавляем клавиатуру с кнопками из списка
                markup = create_keyboard(available_work_buttons)

                logger.info(f"{name} log in")
                await message.answer(f"Привет {name}, ты зарегистрирована.", reply_markup=markup)
                await OrderDeals.waiting_for_modeldeals.set()

    except Exception as exc:
        logger.error(f"Ошибка ввода id - {exc}")
        await message.answer(texts.Hello, reply_markup=types.ReplyKeyboardRemove())
        await OrderDeals.waiting_for_ID.set()