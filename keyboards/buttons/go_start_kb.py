from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app import params_game


buttons_names = params_game.buttons_text["go_start"]
buttons = [KeyboardButton(name) for name in buttons_names]

go_start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True, is_persistent=True)
go_start_keyboard.add(*buttons)
