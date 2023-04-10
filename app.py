from dotenv import load_dotenv, find_dotenv
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import os

load_dotenv(find_dotenv())

storage = MemoryStorage()

bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(bot=bot, storage=storage)
