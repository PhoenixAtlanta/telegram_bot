from aiogram.dispatcher import FSMContext
from random import randint
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher

from random import shuffle

from app import bot, dp, bot_params
from working_data import *
from auxiliary_functions import reset
#* импорт клавиатуры
from keyboards import player_keyboards, professions_keyboard, step_keyboard
from params import all_cards
from auxiliary_functions import create_voting

class FSMAdmin(StatesGroup):  # машина состояния
    team_formation = State()  # образование команды
    go_play = State()  # начало игры
    n_step = State()  # шаг игры
    show_cart = State()  # пользователь показывает одну из карт
    voting = State()  # голосование 
    stop = State()  # завершение игры


key_voting = ["bunker", "admin", "player", "game_over"] 


#* (I) - хендлеры управления игрой 

async def cmd_start_game(message: types.Message, state=FSMContext):


    await FSMAdmin.team_formation.set()

    async with state.proxy() as data:
        data["admin_id"]: int=message.from_user.id

        data["chat_id"]: int=message.chat.id

        data["last_message"]: types.Message=None

        data["players_condition"]: list=[message.from_user.id, ]

        data["players"]: dict={message.from_user.id: {"nickname": message.from_user.full_name, "card": all_cards.copy()}, }

        data["step_player"]: int=0

        data["step"]: int=1

        data["voting"]: dict={
                                "bunker": {"voting_message": None, "start_message": None},
                                "admin": {"voting_message": None, "start_message": None},
                                "player": {"voting_message": None, "start_message": None},
                                "game_over": {"voting_message": None, "start_message": None}
                                }
        day = data.__dict__['_data'].copy()

        await update_chat_data(message.chat.id, day)
    
    await message.answer("Создаем команду, для того чтобы участвовать в игре напишите /i", reply_markup=player_keyboards)
 


#! /go
async def go(message: types.Message, state=FSMContext):

    await last_message(state, message)
    FSMAdmin
    await message.answer("Игра началась!")
    [await bot.send_message(player, text="**ваши карты**") for player in await player_condition_prop(state)]

    await FSMAdmin.next()  # закончилась регистрация, началась игра
    await message.answer("__событие в мире__")
# распределяем игроков случайным образом
    await shuffle_players(state)

    await message.answer(f"первый ходит игрок __{await players_prop(state, key='nickname')}__\nкогда Вы закончите ход напишите команду /all", reply_markup=step_keyboard)
    await next_step(message, state)



async def next_step(message: types.Message, state=FSMContext):
    chat_id = await get_chat_id(state)
    await last_message(state, message)

    if await step_player_prop(state) <= len(await player_condition_prop(state)) - 1:
        await step_player_prop(state, event="1")

        await bot.send_message(chat_id=chat_id, text=f"следующий ходит {await players_prop(state, key='nickname')}")
    
        if await step_prop(state) > 1:
            await bot.send_message(chat_id=chat_id, text="Выберете одну из карт", reply_markup=professions_keyboard)
            #! card

        else:
            await bot.send_message(chat_id=chat_id, text="Выберете карту профессии", reply_markup=professions_keyboard)
            #! card

        await FSMAdmin.show_cart.set()

    else:
        await bot.send_message(chat_id=chat_id, text="круг завершился \n\n Перейдем к голосованию")
        await FSMAdmin.voting.set()
        await bunker_voting(message, state)


async def get_cart(message: types.Message, state=FSMContext):
    await message.answer(f"вы выбрали карту {message.text}\nвремя на описание карты", reply_markup=step_keyboard)
    #! добавить карту в использованные
    await FSMAdmin.voting.set()


async def bunker_voting(message: types.Message, state: FSMContext, player=None):
    await last_message(state, message)

    voting_params = await create_voting(state, topic="Кто не достоин находиться в бункере", variants=(await player_condition_prop(state) if player is None else player), id_people=True)
    await voting_prop(state, type_voting="bunker", chat_id=await get_chat_id(state), event="add", voting_params=voting_params)   


async def bunker_voting_result(quiz_answer: types.PollAnswer, state: FSMContext):
    response = await voting_prop(state, type_voting="bunker") 
    if len(await player_condition_prop(state)) == sum([var["voter_count"] for var in response["options"]]):
        await close_voting(state, message=await last_message(state, event="get"), type_voting="bunker")
        
        result = await voting_result(voting_result=response)

        if len(result) > 1:
            await bunker_voting(message=await last_message(state, event="get"), state=state, player=result)
            return 

        await player_condition_prop(state, event="del", id_player=await get_id_name(state, result[0]))
        await step_prop(state, event="1")

        if await step_prop(state) > 5:
            await bot.send_message(get_chat_id(state), text="игра закончена")
            await state.finish()

        else:
            await step_player_prop(state, event="0")
            await FSMAdmin.n_step.set()
            await next_step(state)

    else:
        return 


async def cancel_handler(message: types.Message, state: FSMContext):
    await last_message(state, message)

    if message.from_user.id == await admin_id_prop(state):
        current_state = await state.get_state()

        if current_state is None: return

        await state.finish()
        await message.reply("Игра закончена по просьбе")

        # сбросить ве значения игры   
    else:
        await message.answer("""Игру может закончить администратор {админ}!
        \n Попросите администратора закончить игру или сами станьте администратором""")

        voting_params = await create_voting(state, topic="Закончить игру", variants=["Да", "Нет"], id_people=False)
        await voting_prop(state, type_voting="game_over", chat_id=message.chat.id, event="add", voting_params=voting_params) 


async def cancel_handler_result(quiz_answer: types.PollAnswer, state=FSMContext):
    response =await voting_prop(state, type_voting="game_over")
    if len(await player_condition_prop(state)) == sum([var["voter_count"] for var in response["options"]]):
        await close_voting(state, message=await last_message(state, event="get"), type_voting="game_over")

        if response["options"][0]["voter_count"] >=  response["options"][0]["voter_count"]:  # да >= нет 
            await last_message(state, "get").answer("по итогам голосования было принято решение закончить игру")
            state.finish()
        else:
            await last_message(state, "get").answer("по итогам голосования, игра продолжается")




#* (II) - хендлеры для работы с пользователем, как с объектом 

#! добавление игроков 
async def append_player(message: types.Message, state=FSMContext):  # +-
    id_player = message.from_user.id

    if any(id_player == player for player in await player_condition_prop(state)):

        await message.reply("{игрок}, Вы уже участвуете!", reply_markup=player_keyboards)

    # написать код ошибки, если игрок не написал боту

    else:  # -
        await players_prop(state, event="add", id_player=id_player, value={"nickname": message.from_user.full_name, "card": all_cards.copy()})

        await player_condition_prop(state, id_player=id_player, event="add")

        await bot.send_message(message.chat.id, text="{игрок}, Вы теперь в игре!\nЕсли вы получили это сообщение, то все хорошо!", reply_markup=player_keyboards)



#! /выйти
async def leave_player(message: types.Message, state=FSMContext):
    id_player = message.from_user.id

    if any(id_player == player for player in await player_condition_prop(state)):
        print("игрок есть")
        await players_prop(state, event="del", id_player=id_player)
        await player_condition_prop(state, event="del", id_player=id_player)

        await message.reply(f"__игрок__, Вы вышли из игры.\nВсего игроков {len(await player_condition_prop(state))}")

    else:
        await message.reply("__имя__, Вы не участвовали")



async def exclude_player(message: types.Message, state: FSMContext):
    if message.from_user.id == await admin_id_prop(state):
        ...
        #! исключить игрока
    
    else:
        voting_params = await create_voting(state, topic=f"Исключить игрока __игрок__", variants=["Исключить", "Оставить"], id_people=False)
        await voting_prop(state, type_voting="player", chat_id=message.chat.id, event="add", voting_params=voting_params) 


async def exclude_player_result(voting: types.PollAnswer, state: FSMContext):
    response = await voting_prop(state, type_voting="player")
    if len(await player_condition_prop(state)) == sum([var["voter_count"] for var in response["options"]]):
        await close_voting(state, message=await last_message(state, event="get"), type_voting="player")

        if response["options"][0]["voter_count"] >=  response["options"][0]["voter_count"]:  # исключить >= Оставить 
            await last_message(state, "get").answer("по итогам голосования было принято решение Исключить игрока")
            state.finish()
        else:
            await last_message(state, "get").answer("по итогам голосования было принято оставить игрока ")




#* (III) - хендлеры длс работы пользователя с программой, для получения информации 


#! help
async def get_help(message: types.Message, state=FSMContext):
    await message.reply("***доки*** для игры")


#! /кто играет
async def get_players(message: types.Message, state=FSMContext):
    mes = "\n".join([f"{num + 1} - {player}" for num, player in enumerate(await player_condition_prop(state))])
    await message.reply(f"Всего участников {len(await player_condition_prop(state))}\n\n{mes}")


async def change_admin(message: types.Message, state=FSMContext):
    await last_message(state, message)
    voting_params = await create_voting(state, topic="Кто будет администратором игры", variants=await player_condition_prop(state), id_people=True)
    await voting_prop(state, type_voting="admin", chat_id=await last_message(state, event="get").chat.id, event="add", voting_params=voting_params)   


async def change_admin_result(voting: types.PollAnswer, state=FSMContext):
    response = await voting_prop(state, type_voting="admin")

    if len(await player_condition_prop(state)) == sum([var["voter_count"] for var in response["options"]]):
        await close_voting(state, message=await last_message(state, event="get"), type_voting="admin")
        result = await voting_result(voting_result=response, response_type="name")

        if len(result) > 1 or await get_id_name(state, result[0]) == await admin_id_prop(state):
            await bot.send_message(await get_chat_id(state), text="__игрок__, остается администратором")

            return 

        await admin_id_prop(state, event=await get_id_name(state, name=result[0]))
        await bot.send_message(await get_chat_id(state), text="__игрок__, становится администратором, по итогам голосования")


#* (IV) - методы

async def hello(message: types.Message):
    cur_state = dp.current_state()
    async with cur_state.proxy() as data:
        print(data)


async def definition_voting(voting):
    print("qqq")
    # id_answer = voting["poll_id"]
    try:
        cur_state = dp.current_state()
        print(3)
        async with cur_state.proxy() as data:
            num = str(randint(0, 100))
            print(1)
            data["count" + num] = num
            print(data, "q")
            print(2)
    except Exception as e:
        print(e)
    # try:
    #     async with state.proxy() as data:
    #         print(data)
    #         print(1)
    #         for key in data["voting"]:
    #             print(2)
    #             print(data["voting"])
    #             print(key)
    #             print(data["voting"][key])
    #             print(3)
    #             id_voting = await voting_prop(state, type_voting=key)["poll"]["id"]
    #             if id_answer == id_voting:

    #                 if key == "bunker":
    #                     print('bunker')
    #                     await bunker_voting_result(voting, state=state)

    #                 if key == "game_over":
    #                     await cancel_handler_result(voting, state=state)

    #                 if key == "player":
    #                     await exclude_player_result(voting, state=state)

    #                 if key == "admin":
    #                     await change_admin_result(voting, state=state)
    # except Exception as e:
    #     print(e, "ошибка")


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
    dp.register_message_handler(bunker_voting, commands=["vot"], state=FSMAdmin)

    dp.register_poll_answer_handler(definition_voting)
    # dp.register_poll_answer_handler(change_admin_result)
    # dp.register_poll_answer_handler(bunker_voting_result)
    # dp.register_poll_answer_handler(cancel_handler_result)
    # dp.register_poll_answer_handler(exclude_player_result)

    dp.register_message_handler(cancel_handler, commands=["stop"], state="*")

    dp.register_message_handler(append_player, commands=["i"], state="*")
    dp.register_message_handler(leave_player, commands=["выйти", "leave"], state="*")
    dp.register_message_handler(exclude_player, commands=["изгнать"], state="*")

    dp.register_message_handler(get_help, commands=["help"], state="*")
    dp.register_message_handler(get_players, commands=["кто", "who"], state="*")
    