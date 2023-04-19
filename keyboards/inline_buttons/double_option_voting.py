from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

yes_button = InlineKeyboardButton("да", callback_data="yes")
no_button = InlineKeyboardButton("нет", callback_data="no")


double_inline_keyboard = InlineKeyboardMarkup().add(yes_button, no_button)
