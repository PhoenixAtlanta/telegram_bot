from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..inline_buttons.create_inline_buttons import create_inline

double_inline_value = {"да": {"number": 0, "callback": "да"}, "нет": {"number": 0, "callback": "нет"}}
try:
    print(create_inline(double_inline_value, type_placement="add"))
    double_inline_keyboard = create_inline(double_inline_value, type_placement="add")
except Exception as e:
    print(e)


