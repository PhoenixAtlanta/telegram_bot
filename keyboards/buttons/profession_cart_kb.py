from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button = KeyboardButton("Профессия")

profession_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

profession_keyboard.add(button)
