from dotenv import load_dotenv, find_dotenv
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from params import set_params

import os

load_dotenv(find_dotenv())

storage = MemoryStorage()

bot_params = set_params()
print(bot_params)

bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(bot=bot, storage=storage)
