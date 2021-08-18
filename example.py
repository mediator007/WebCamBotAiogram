import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.bot_command import BotCommand
import config1

available_food_names = ["суши", "спагетти", "хачапури"]
available_food_sizes = ["маленькую", "среднюю", "большую"]

class OrderFood(StatesGroup):
    waiting_for_food_name = State()
    waiting_for_food_size = State()

async def food_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_food_names:
        keyboard.add(name)
    await message.answer("Выберите блюдо:", reply_markup=keyboard)
    await OrderFood.waiting_for_food_name.set()

async def food_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_food_names:
        await message.answer("Пожалуйста, выберите блюдо, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_food=message.text.lower())#######!!!!!!!!

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in available_food_sizes:
        keyboard.add(size)
    # Для последовательных шагов можно не указывать название состояния, обходясь next()
    await OrderFood.next()
    await message.answer("Теперь выберите размер порции:", reply_markup=keyboard)

async def food_size_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() not in available_food_sizes:
        await message.answer("Пожалуйста, выберите размер порции, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    await message.answer(f"Вы заказали {message.text.lower()} порцию {user_data['chosen_food']}.\n"
                         f"Попробуйте теперь заказать напитки: /drinks", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Выберите, что хотите заказать: напитки (/drinks) или блюда (/food).",
        reply_markup=types.ReplyKeyboardRemove()
    )

async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())

def register_handlers_food(dp: Dispatcher):
    dp.register_message_handler(food_start, commands="food", state="*")
    dp.register_message_handler(food_chosen, state=OrderFood.waiting_for_food_name)
    dp.register_message_handler(food_size_chosen, state=OrderFood.waiting_for_food_size)
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    #dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")

############################################
############################################
############################################


logger = logging.getLogger(__name__)

# Регистрация команд, отображаемых в интерфейсе Telegram
async def set_commands(bot: Bot):
    commands = [BotCommand(command="/food", description="Заказать блюда")]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    bot = Bot(token=config1.token)
    dp = Dispatcher(bot, storage=MemoryStorage())
    # Регистрация хэндлеров
    #register_handlers_common(dp)
    #register_handlers_drinks(dp)
    register_handlers_food(dp)
    await set_commands(bot)
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())