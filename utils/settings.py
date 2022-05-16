from aiogram import Bot
from aiogram import Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils.config import token


bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())