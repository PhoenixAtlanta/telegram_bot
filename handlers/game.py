from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher

from random import shuffle

from app import bot, dp, bot_params
from working_data import working_json
from auxiliary_functions import reset
#* импорт клавиатуры
from keyboards import player_keyboards, professions_keyboard, step_keyboard


class FSMAdmin(StatesGroup):  # машина состояния
    team_formation = State()  # образование команды
    go_play = State()  # начало игры
    n_step = State()  # шаг игры
    show_cart = State()  # пользователь показывает одну из карт
    voting = State()  # голосование 
    stop = State()  # завершение игры



# (I) - хендлеры управления игрой 
# (II) - хендлеры для работы с пользователем, как с объектом 
# (III) - хендлеры длс работы пользователя с программой, для получения информации 
# (IV) - методы

#* (I) - хендлеры управления игрой 

async def cmd_start_game(message: types.Message, state=FSMContext):
    # working_json.writing_admin(message.from_user.id)

    await FSMAdmin.team_formation.set()

    async with state.proxy() as data:
        data["admin_id"] = message.from_user.id

        data["players_condition"] = [message.from_user.id, ]

        data["players"] = {message.from_user.id: {"nickname": message.from_user.full_name, "used_card": []}, }

        data["step_player"] = 0

        data["step"] = 0
    
    await message.answer("Создаем команду, для того чтобы участвовать в игре напишите /i", reply_markup=player_keyboards)


#! /go
async def go(message: types.Message, state=FSMContext):
    await message.answer("Игра началась!")
    try:
        [await bot.send_message(player, text="**ваши карты**") for player in get_players(state)]

        await FSMAdmin.next()  # закончилась регистрация, началась игра
        await message.answer("__событие в мире__")
  # распределяем игроков случайным образом
        shuffle_players(state)

        await message.answer(f"первый ходит игрок __{await get_now_player(state)}__\nкогда Вы закончите ход напишите команду /all")
        await next_step(message, state)
    except Exception as e:
        print(e)


async def next_step(message: types.Message, state=FSMContext):
    if property_step_player(state) <= len(get_players) - 1:
        await property_step_player(state, event="1")


        await message.answer(f"следующий ходит {await get_now_player(state)}")
        
        if property_step_player(state) > 1:
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
    await FSMAdmin.voting.set()


async def voting(message: types.Message, state: FSMContext):
    await message.answer("прошло голосование")

    await property_step_player(state, event="1")
    
    if await property_next_step(state) >= 5:
        await message.answer("игра закончена")
        await state.finish()

    else:
        await property_step_player(state, event="0")
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

    if any(id_player == player for player in get_players(state)):

        await message.reply("{игрок}, Вы уже участвуете!", reply_markup=player_keyboards)

    # написать код ошибки, если игрок не написал боту

    else:  # -
        try:

            bot_params["params_game"].players.append([id_player, message.from_user.full_name])  # +
            await bot.send_message(message.chat.id, text="{игрок}, Вы теперь в игре!\nЕсли вы получили это сообщение, то все хорошо!", reply_markup=player_keyboards)
        except Exception as e:
            print(e)


#! /выйти
async def leave_player(message: types.Message, state=FSMContext):
    id_player = message.from_user.id

    if any(id_player == player[0] for player in bot_params["params_game"].players):
        bot_params["params_game"].players.remove([id_player, message.from_user.full_name])
        await message.reply(f"__игрок__, Вы вышли из игры.\nВсего игроков {len(bot_params['params_game'].players)}")

    else:
        await message.reply("Вы не участвовали")


async def exclude_player(message: types.Message, state: FSMContext):
    if message.from_user.id == bot_params["params_game"].ID:
        for id_p, nickname in bot_params["params_game"].players:

            if nickname in message.text:
                bot_params["params_game"].players.remove([id_p, nickname])
                message.reply(f"Игрок {nickname} был исключен по просьбе администратора")
    
    else:
        ...
        #! по голосованию


#* (III) - хендлеры длс работы пользователя с программой, для получения информации 


#! help
async def get_help(message: types.Message, state=FSMContext):
    await message.reply("***доки*** для игры")


#! /кто играет
async def get_players(message: types.Message, state=FSMContext):
    mes = "\n".join([f"{num + 1} - {player}" for num, player in enumerate(bot_params["params_game"].players)])
    await message.reply(f"Всего участников {len(bot_params['params_game'].players)}\n\n{mes}")

#* (IV) - методы


async def admin_id_prop(state, event=None):
    """получить id админа или установить новое"""
    async with state.proxy() as data:
        if event is None:
            return data["admin_id"]

        else:
            data["admin_id"] = event


async def players_prop(state, id_player: int=0, key: str="", value=None, event=None):
    """получить данные игрока или записать"""
    async with state.proxy() as data:

        if event is None:  # вернуть значение по ключу
            return data["players"][id_player][key]
        
        elif key == "card":  # удалить карту из списка
            cards = data["players"][id_player][key]
            cards.remove(value)
            data["players"][id_player][key] = cards
        
        elif event == "key":  # изменить элемент
            data["players"][id_player][key] = value

        elif event == "add":  # добавить игрока
            data["players"][value["id"]] = {"nick_name": value["nick_name"], "card": []}

        elif event == "del":  # удалить игрока
            keys = list(data["players"].keys())
            keys.remove(id_player)
            new_dict = {}

            for key in keys:
                new_dict[keys] = data["players"][keys]

            data["players"] = new_dict.copy()
            del new_dict
        

async def step_player_prop(state, event:str="get"):
    """получить или установить новое значение следующего игрока"""

    async with state.proxy() as data:
        if event == "get":
            return data["step_player"]

        elif event == "1":
            data["step_player"] += 1

        elif event == "0":
            data["step_player"] = 0



async def step_prop(state, event=None):
    async with state.proxy() as data:
        if event is None:
            return data["step"]
        
        elif event == "1":
            data["step"] += 1


async def player_condition_prop(state, id_player: int, event=None, ):
    async with state.proxy() as data:
        if event is None:
            return data["players_condition"]
        
        elif event == "add":
            data["players_condition"].append(id_player)

        elif event == "del":
            data["players_condition"].remove(id_player)


async def get_player(state):
    """получить id текущего игрока"""
    async with state.proxy() as data:
        return data["players_condition"][step_player_prop(state)]
    

async def shuffle_players(state):
    """поменять порядок игроков"""
    async with state.proxy() as data:
        data["players_condition"] = shuffle(data["players_condition"])


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
    