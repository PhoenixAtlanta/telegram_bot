from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from dataclasses import dataclass, field
from typing import List
from random import shuffle

from app import bot, dp, bot_params
from auxiliary_functions import reset
#* импорт клавиатуры


class FSMAdmin(StatesGroup):
    team_formation = State()
    go_play = State()
    n_step = State()
    show_cart = State()
    voting = State()
    stop = State()



async def get_player(players: list=bot_params["params_game"].players, index: int=bot_params["params_game"].player) -> int:
    return players[index]



async def cmd_start_game(message: types.Message):
    bot_params["params_game"].ID = message.from_user.id
    await FSMAdmin.team_formation.set()
    await message.answer("Создаем команду, для того чтобы участвовать в игре напишите /i")
    bot_params["params_game"].players.append([message.from_user.id, message.from_user.first_name])
    
    # try:
    #     await bot.send_message(message.from_user.id, text=bot_params["params_game"].ID)
    #     print(bot_params["params_game"].ID)
    # except Exception as e:
    #     print(e)

async def exclude_player(message: types.Message, state: FSMContext):
    if message.from_user.id == bot_params["params_game"].ID:
        for id_p, nickname in bot_params["params_game"].players:

            if nickname in message.text:
                bot_params["params_game"].players.remove([id_p, nickname])
                message.reply(f"Игрок {nickname} был исключен по просьбе администратора")
    
    else:
        ...
        #! по голосованию



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
        #! сделать голосование 


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
    await message.answer("__событие в мире__")

    shuffle(bot_params["params_game"].players)  # распределяем игроков случайным образом

    await message.answer(f"первый ходит игрок __{await get_player()}__\nкогда Вы закончите ход напишите команду /all")
    await next_step(message, state)

    
async def next_step(message: types.Message, state=FSMContext):

    if bot_params["params_game"].player + 1 <= len(bot_params["params_game"].players):
        bot_params["params_game"].player += 1

        await message.answer(f"следующий ходит {get_player()}")
        
        if bot_params["params_game"].step > 1:
            await message.answer("Выберете одну из карт")

        else:
            await message.answer("Выберете карту профессии")

        await FSMAdmin.show_cart.set()

    else:
        await message.answer("круг завершился \n\n Перейдем к голосованию")
        await FSMAdmin.voting.set()
        await voting(message, state)


async def get_cart(message: types.Message, state=FSMContext):
    await message.answer(f"вы выбрали карту {message.text}\nвремя на описание карты")
    await FSMAdmin.voting.set()


async def voting(message: types.Message, state: FSMContext):
    await message.answer("прошло голосование")
    bot_params["params_game"].step += 1

    if bot_params["params_game"].step >= 5:
        await message.answer("игра закончена")
        await state.finish()

    else:
        bot_params["params_game"].player = 0
        await message.answer(f"ходит игрок {get_player()}")
        await FSMAdmin.n_step.set()

    


#// проверить help
#? написать бота, и проверить добавление игроков
#// кто играет
#// выйти
#// /go
#? выгнать игрока


def register_handler_game(dp: Dispatcher):
    dp.register_message_handler(cmd_start_game, commands=["start"])
    dp.register_message_handler(cancel_handler, commands=["stop"], state="*")

    dp.register_message_handler(cancel_handler, commands=["stop"], state="*")

    dp.register_message_handler(get_help, commands=["help"], state="*")
    dp.register_message_handler(append_player, commands=["i"], state="*")
    dp.register_message_handler(get_players, commands=["кто", "who"], state="*")
    dp.register_message_handler(leave_player, commands=["выйти", "leave"], state="*")
    
    dp.register_message_handler(go, commands=["go"], state=FSMAdmin.team_formation)
    dp.register_message_handler(next_step, commands=["all"], state=FSMAdmin)
    dp.register_message_handler(get_cart, commands=["cart"], state=FSMAdmin)
    dp.register_message_handler(voting, commands=["vot"], state=FSMAdmin)
