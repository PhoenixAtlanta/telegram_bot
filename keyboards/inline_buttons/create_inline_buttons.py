from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_inline(data_buttons: dict, type_placement: str="add"):
    buttons = [InlineKeyboardButton(f"{key} - {data_buttons[key]['number']}", callback_data=data_buttons[key]["callback"]) for key in data_buttons]

    keyboard = InlineKeyboardMarkup()

    if type_placement == "row":
        keyboard.row(*buttons)
    
    else:
        keyboard.add(*buttons)

    return keyboard

