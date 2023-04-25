from aiogram import types, Dispatcher
import working_data

from app import bot


async def cmd_start(message: types.Message):
    await bot.send_message(message.from_user.id, text=working_data.dialog("main_help"))



def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["help"])
    