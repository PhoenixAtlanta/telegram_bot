from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from params import buttons_name


buttons_names = buttons_name["player_buttons"]
buttons = [KeyboardButton(name) for name in  buttons_names]

player_keyboards = ReplyKeyboardMarkup(resize_keyboard=True)
player_keyboards.add(*buttons)
