from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def create_all_cart_keyboard(cart: list):
    buttons = [KeyboardButton(name) for name in cart]   
    all_cart_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    all_cart_keyboard.add(*buttons)

    return all_cart_keyboard
