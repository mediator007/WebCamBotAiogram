import asyncio
import sqlite3
from aiogram import Bot
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup
from aiogram.types.bot_command import BotCommand
from aiogram_calendar import simple_cal_callback, SimpleCalendar
# from aiogram_bot.misc import bot, dp
from loguru import logger

from utils.config import token
from utils import messages as texts
from utils.local_vars import available_admin_buttons
from utils.functions import OrderDeals

from handlers.model import model_deals
from handlers.identification import identification
from handlers.bot_start import bot_start

from utils.settings import dp, bot

# bot = Bot(token=token)
# dp = Dispatcher(bot, storage=MemoryStorage())
start_kb = ReplyKeyboardMarkup(resize_keyboard=True,)


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

    elif message.text.lower() == available_admin_buttons[1]:
        await message.answer("Введите имя")
        await OrderDeals.waiting_for_modeldelete.set()

    elif message.text.lower() == available_admin_buttons[2]:
        await message.answer("Введите свой ID")
        await OrderDeals.waiting_for_ID.set()


@dp.callback_query_handler(simple_cal_callback.filter(), state=OrderDeals.waiting_for_date)
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    # print(callback_query, callback_data)
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    # print(date)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}',
            reply_markup=start_kb
        )
        await OrderDeals.waiting_for_admindeals.set()


async def model_delete(message: types.Message, state: FSMContext):
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
