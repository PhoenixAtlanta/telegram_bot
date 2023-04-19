from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from params import buttons_name


buttons_name = buttons_name["step"]

buttons = [KeyboardButton(name) for name in buttons_name]

step_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

step_keyboard.add(*buttons)




