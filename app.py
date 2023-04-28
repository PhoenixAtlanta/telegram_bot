import os

from dotenv import load_dotenv, find_dotenv
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.json_data_work import DataJson
from params import ParamGame


load_dotenv(find_dotenv())  # получить файл .env
storage = MemoryStorage()  # состояние fsm машины

json_data_base = DataJson()  # база данных карт
params_game = ParamGame()   # параметры заполнения игры
bot = Bot(os.getenv("TOKEN"))  # запустить бота
dp = Dispatcher(bot=bot, storage=storage)
