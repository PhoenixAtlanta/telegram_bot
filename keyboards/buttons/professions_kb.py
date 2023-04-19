from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from params import buttons_name

buttons_name = buttons_name["card"]

buttons = [KeyboardButton(name) for name in buttons_name]

professions_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

professions_keyboard.add(*buttons)
