from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..inline_buttons.create_inline_buttons import create_inline_buttons

double_inline_value = {"да": {"number": 0, "callback": "yes"}, "нет": {"number": 0, "callback": "no"}}

double_inline_keyboard = create_inline_buttons(double_inline_value, type_placement="add")

