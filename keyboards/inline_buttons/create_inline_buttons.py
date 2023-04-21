from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def create_inline_buttons(data_buttons: dict, type_placement: str="add"):
    buttons = [InlineKeyboardButton(f"{key} - {data_buttons[key]['number']}", callback_data=data_buttons[key]["callback"]) for key in data_buttons]

    if type_placement == "row":

        return InlineKeyboardMarkup().row(*buttons)
    
    else:
        return InlineKeyboardMarkup().add(*buttons)

