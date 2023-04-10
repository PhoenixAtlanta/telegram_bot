from aiogram import types, Dispatcher

from app import bot, dp


async def cmd_start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, text="Привет")
    except Exception as a:
        print(a)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    