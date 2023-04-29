from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# кнопки доступных крат игрока
def create_carts_buttons(carts: list[str]) -> ReplyKeyboardMarkup:
    buttons = [KeyboardButton(name) for name in carts]
    carts_spec_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    carts_spec_keyboard.add(*buttons)

    return carts_spec_keyboard
