from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button = KeyboardButton("/go")

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(button)
