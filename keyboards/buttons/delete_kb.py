from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button = KeyboardButton("/delete")

delete_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

delete_keyboard.add(button)
