from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher

from random import shuffle

from app import bot, dp, bot_params
from working_data import *
from auxiliary_functions import reset
#* импорт клавиатуры
from keyboards import player_keyboards, professions_keyboard, step_keyboard
from params import all_cards

class FSMAdmin(StatesGroup):  # машина состояния
    team_formation = State()  # образование команды
    go_play = State()  # начало игры
    n_step = State()  # шаг игры
    show_cart = State()  # пользователь показывает одну из карт
    voting = State()  # голосование 
    stop = State()  # завершение игры


#* (I) - хендлеры управления игрой 

async def cmd_start_game(message: types.Message, state=FSMContext):

    await FSMAdmin.team_formation.set()

    async with state.proxy() as data:
        data["admin_id"] = message.from_user.id

        data["players_condition"] = [message.from_user.id, ]

        data["players"] = {message.from_user.id: {"nickname": message.from_user.full_name, "card": all_cards.copy()}, }

        data["step_player"] = 0

        data["step"] = 1
    
    await message.answer("Создаем команду, для того чтобы участвовать в игре напишите /i", reply_markup=player_keyboards)


#! /go
async def go(message: types.Message, state=FSMContext):
    await message.answer("Игра началась!")
    [await bot.send_message(player, text="**ваши карты**") for player in await player_condition_prop(state)]

    await FSMAdmin.next()  # закончилась регистрация, началась игра
    await message.answer("__событие в мире__")
# распределяем игроков случайным образом
    await shuffle_players(state)

    await message.answer(f"первый ходит игрок __{await players_prop(state, key='nickname')}__\nкогда Вы закончите ход напишите команду /all", reply_markup=step_keyboard)
    await next_step(message, state)



async def next_step(message: types.Message, state=FSMContext):
    if await step_player_prop(state) <= len(await player_condition_prop(state)) - 1:
        await step_player_prop(state, event="1")


        await message.answer(f"следующий ходит {await players_prop(state, key='nickname')}")
    
        if await step_prop(state) > 1:
            await message.answer("Выберете одну из карт", reply_markup=professions_keyboard)
            #! card

        else:
            await message.answer("Выберете карту профессии", reply_markup=professions_keyboard)
            #! card

        await FSMAdmin.show_cart.set()


    else:
        await message.answer("круг завершился \n\n Перейдем к голосованию")
        await FSMAdmin.voting.set()
        await voting(message, state)


async def get_cart(message: types.Message, state=FSMContext):
    await message.answer(f"вы выбрали карту {message.text}\nвремя на описание карты", reply_markup=step_keyboard)
    #! добавить карту в использованные
    await FSMAdmin.voting.set()


async def voting(message: types.Message, state: FSMContext):
    await message.answer("прошло голосование")
    #!голосование

    await step_prop(state, event="1")
    
    if await step_prop(state) > 5:
        await message.answer("игра закончена")
        await state.finish()

    else:
        await step_player_prop(state, event="0")
        await FSMAdmin.n_step.set()
        await next_step(message, state)


async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == await admin_id_prop(state):
        current_state = await state.get_state()

        if current_state is None: return

        await state.finish()
        await message.reply("Игра закончена по просьбе")

        # сбросить ве значения игры   
    else:
        await message.answer("""Игру может закончить администратор {админ}!
        \n Попросите администратора закончить игру или сами станьте администратором""")
        #! сделать голосование 


#* (II) - хендлеры для работы с пользователем, как с объектом 

#! добавление игроков 
async def append_player(message: types.Message, state=FSMContext):  # +-
    id_player = message.from_user.id

    if any(id_player == player for player in await player_condition_prop(state)):

        await message.reply("{игрок}, Вы уже участвуете!", reply_markup=player_keyboards)

    # написать код ошибки, если игрок не написал боту

    else:  # -
        try:
            await players_prop(state, event="add", id_player=id_player, value={"nickname": message.from_user.full_name, "card": all_cards.copy()})

            await player_condition_prop(state, id_player=id_player, event="add")
            print(await player_condition_prop(state))

            await bot.send_message(message.chat.id, text="{игрок}, Вы теперь в игре!\nЕсли вы получили это сообщение, то все хорошо!", reply_markup=player_keyboards)
        except Exception as e:
            print(e)


#! /выйти
async def leave_player(message: types.Message, state=FSMContext):
    id_player = message.from_user.id
    try:

        if any(id_player == player for player in await player_condition_prop(state)):
            print("игрок есть")
            await players_prop(state, event="del", id_player=id_player)
            await player_condition_prop(state, event="del", id_player=id_player)

            await message.reply(f"__игрок__, Вы вышли из игры.\nВсего игроков {len(await player_condition_prop(state))}")

        else:
            await message.reply("__имя__, Вы не участвовали")

    except Exception as e:
        print(e)


async def exclude_player(message: types.Message, state: FSMContext):
    if message.from_user.id == await admin_id_prop(state):
        ...
        #! исключить игрока
    
    else:
        ...
        #! по голосованию


#* (III) - хендлеры длс работы пользователя с программой, для получения информации 


#! help
async def get_help(message: types.Message, state=FSMContext):
    await message.reply("***доки*** для игры")


#! /кто играет
async def get_players(message: types.Message, state=FSMContext):
    mes = "\n".join([f"{num + 1} - {player}" for num, player in enumerate(await player_condition_prop(state))])
    await message.reply(f"Всего участников {len(await player_condition_prop(state))}\n\n{mes}")

#* (IV) - методы




#// проверить help
#? написать бота, и проверить добавление игроков
#// кто играет
#// выйти
#// /go
#? выгнать игрока


def register_handler_game(dp: Dispatcher):
    dp.register_message_handler(cmd_start_game, commands=["start"])
    dp.register_message_handler(go, commands=["go"], state=FSMAdmin.team_formation)
    dp.register_message_handler(next_step, commands=["all"], state=FSMAdmin)
    dp.register_message_handler(get_cart, commands=["cart"], state=FSMAdmin)
    dp.register_message_handler(voting, commands=["vot"], state=FSMAdmin)
    dp.register_message_handler(cancel_handler, commands=["stop"], state="*")

    dp.register_message_handler(append_player, commands=["i"], state="*")
    dp.register_message_handler(leave_player, commands=["выйти", "leave"], state="*")
    dp.register_message_handler(exclude_player, commands=["изгнать"], state="*")

    dp.register_message_handler(get_help, commands=["help"], state="*")
    dp.register_message_handler(get_players, commands=["кто", "who"], state="*")
    