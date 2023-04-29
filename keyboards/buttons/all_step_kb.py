from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app import params_game


# кнопка для, чтобы оповестить что ход законен
buttons_names = params_game.buttons_text["all_step"]
buttons = [KeyboardButton(name) for name in buttons_names]

all_step_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
all_step_keyboard.add(*buttons)
