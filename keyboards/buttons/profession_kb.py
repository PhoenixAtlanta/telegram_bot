from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app import params_game


buttons_names = params_game.buttons_text["profession"]
buttons = [KeyboardButton(name) for name in buttons_names]

profession_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
profession_keyboard.add(*buttons)
