from aiogram import types, Dispatcher
from aiogram.types import InputFile

from data import dialog  # создание диалога
from app import bot, params_game, json_data_base


# получить помощь по боту, пока не запущена fsm машина
async def cmd_start(message: types.Message,):  
    await bot.send_message(message.from_user.id, text=dialog("main_help"))


# отравить пользователю, все карты характеристики его персонажа
async def generate_cart(message: types.Message):
        if message.chat.type == "private":
            id_player = message.from_user.id
            for type_cart in params_game.cart_for_game:
                image_data = json_data_base.get_random_cart(type_cart)
                photo = InputFile(image_data["path_to_image"])

                await bot.send_photo(chat_id=id_player, photo=photo)
                await bot.send_message(
                    chat_id=id_player,
                    text=f"""Тип карты:\n{image_data['description'].split(';')[0]}
                    \nНазвание карты:\n{image_data['description'].split(';')[1]}
                    \nОписание:\n{image_data['description'].split(';')[-1]}""")
        else:
            await message.reply("""Бот раздает карты только в личных
 сообщениях @BunkerGameBot_bot по команде /carts.""")


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["help"])
    dp.register_message_handler(generate_cart, commands=["carts"], state="*")

