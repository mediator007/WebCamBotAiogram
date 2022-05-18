import sqlite3
from aiogram import Dispatcher, types
from loguru import logger

from utils.functions import OrderDeals
from utils.db_requests import (
    name_by_input_id, 
    name_by_chat_id,
    search_admin_for_reboot,
    )
from utils.local_vars import available_admin_buttons, available_work_buttons
from utils.db_requests import update_chat_id_in_registration
from utils import messages as texts


async def bot_start(message):
    """
    Функция первоначального запуска бота или ребута
    """
    chat_id = message.from_user.id

    # Проверка на наличие chat_id в бд моделей для реконнекта 
    with sqlite3.connect("database.db") as conn:
        result_model = name_by_chat_id(conn, chat_id)
    
    # Проверка наличия chat_id в бд админов для реконнекта
    result_admin = search_admin_for_reboot(chat_id)
    
    # если модель есть в бд - восстанавливаем сессию
    if result_model:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in available_work_buttons:
            markup.add(name)
        await message.answer("Сессия модели восстановлена.", reply_markup=markup)
        logger.info(f"Сессия восстановлена для id {chat_id}")
        await OrderDeals.waiting_for_modeldeals.set()

    # Если админ есть в бд
    elif result_admin:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in available_admin_buttons:
            markup.add(name)
        await message.answer("Сессия администратора восстановлена.", reply_markup=markup)
        logger.info(f"Сессия администратора восстановлена для id {chat_id}")
        await OrderDeals.waiting_for_admindeals.set()

    # если нет в бд ожидаем ввод id
    else:
        await message.answer(texts.Hello, reply_markup=types.ReplyKeyboardRemove())
        await OrderDeals.waiting_for_ID.set()