from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from dataclasses import dataclass, field
from typing import List

from app import bot, dp, bot_params
from auxiliary_functions import reset
#* импорт клавиатуры


class FSMAdmin(StatesGroup):
    team_formation = State()
    go_play = State()


async def cmd_start_game(message: types.Message):
    bot_params["params_game"].ID = message.from_user.id
    await FSMAdmin.team_formation.set()
    await message.answer("Создаем команду, для того чтобы участвовать в игре напишите /i")
    bot_params["params_game"].players.append(message.from_user.id)
    
    # try:
    #     await bot.send_message(message.from_user.id, text=bot_params["params_game"].ID)
    #     print(bot_params["params_game"].ID)
    # except Exception as e:
    #     print(e)


async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == bot_params["params_game"].ID:
        current_state = await state.get_state()

        if current_state is None: return

        await state.finish()
        await message.reply("Игра закончена по просьбе")

        # сбросить ве значения игры
        bot_params["params_game"] = reset.reset_params(bot_params["params_game"])
   
    else:
        await message.answer("""Игру может закончить администратор {админ}!
        \n Попросите администратора закончить игру или сами станьте администратором""")


#! help
async def get_help(message: types.Message, state=FSMContext):
    await message.reply("***доки*** для игры")


#! добавеление игракав 
async def append_player(message: types.Message, state=FSMContext):  # +-
    id_player = message.from_user.id

    if id_player in bot_params["params_game"].players:  # +
        await message.reply("{игрок}, Вы уже участвуете!")

    # написать код ошибки, если игрок не написал боту

    else:  # -
        bot_params["params_game"].players.append(id_player)  # +
        await message.reply("{игрок}, Вы теперь в игре!")
        await bot.send_message(message.from_user.id, text="Если вы получили это сообщение, то все хорошо!")
    

#! /кто играет
async def get_players(message: types.Message, state=FSMContext):
    mes = "\n".join([f"{num + 1} - {player}" for num, player in enumerate(bot_params["params_game"].players)])
    await message.reply(f"Всего участников {len(bot_params['params_game'].players)}\n\n{mes}")
    

#! /выйти
async def leave_player(message: types.Message, state=FSMContext):
    id_player = message.from_user.id

    if id_player in bot_params["params_game"].players:
        bot_params["params_game"].players.remove(id_player)
        await message.reply(f"__игрок__, Вы вышли из игры.\nВсего игроков {len(bot_params['params_game'].players)}")

    else:
        await message.reply("Вы не участвовали")


#! /go
async def go(message: types.Message, state=FSMContext):
    await message.answer("Игра началась!")

    for player in bot_params['params_game'].players:
        await bot.send_message(player, "**ваши карты**")

    await FSMAdmin.next()  # закончилась регистрация, началась игра
    await state.finish()
    await print("игра завершилась")


#// проверить help
#? написать бота, и проверить добавление игроков
#// кто играет
#// выйти
#// /go


def register_handler_game(dp: Dispatcher):
    dp.register_message_handler(cmd_start_game, commands=["start"])
    dp.register_message_handler(cancel_handler, commands=["stop"], state="*")
    dp.register_message_handler(get_help, commands=["help"], state="*")
    dp.register_message_handler(append_player, commands=["i"], state="*")
    dp.register_message_handler(get_players, commands=["кто", "who"], state="*")
    dp.register_message_handler(leave_player, commands=["выйти", "leave"], state="*")
    dp.register_message_handler(go, commands=["go"], state=FSMAdmin.team_formation)
