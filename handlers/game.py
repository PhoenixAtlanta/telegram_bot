from aiogram.dispatcher import FSMContext
from random import randint
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from pprint import pprint 

from random import shuffle

from app import bot, dp, bot_params
from working_data import *
from auxiliary_functions import reset

#* импорт клавиатуры
# from keyboards import inline_buttons
import keyboards

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
        try:
            data["current_player"]: int=0
 
            data["number_step"]: int=1

            data["admin_id"]: int=message.from_user.id

            data["chat_id"]: int=message.chat.id


            data["players_condition"]: list=[message.from_user.id, ]

            data["candidates"]: list=[]


            data["players"]: dict={message.from_user.id: {"nickname": message.from_user.username, "card": all_cards.copy()}}

            data["voting"]: dict={
                                    "bunker": {},  # сделать метод, который будет создавать пустой шаблон
                                    "admin": {},
                                    "player": {},
                                    "game_over": {}
                                    }
            
        except Exception as e:
            print(e)
                        
    await message.answer("Создаем команду, для того чтобы участвовать в игре напишите /i", reply_markup=keyboards.player_keyboards)



#! /go
async def go(message: types.Message, state=FSMContext):

    await message.answer("Игра началась!")
    [await bot.send_message(player, text="**ваши карты**") for player in await players_condition_prop(state)]

    await FSMAdmin.next()  # закончилась регистрация, началась игра
    await message.answer("__событие в мире__")
# распределяем игроков случайным образом
    await shuffle_players(state)

    await message.answer(f"первый ходит игрок {await players_prop(state, param='nickname')}\nкогда Вы закончите ход напишите команду /all", reply_markup=keyboards.step_keyboard)
    await next_step(message, state)


async def next_step(message: types.Message, state=FSMContext):
    if await current_player_prop(state) <= len(await players_condition_prop(state)) - 1:
        await current_player_prop(state, value=await current_player_prop(state) + 1)

        await message.answer(f"следующий ходит {await players_prop(state, key='nickname')}")
    
        if await number_step_prop(state) > 1:
            await message.answer("__player__. Выберете одну из карт", reply_markup=keyboards.professions_keyboard)
            #! card

        else:
            await message.answer(" __player__. Выберете карту профессии", reply_markup=keyboards.professions_keyboard)
            #! card
        await FSMAdmin.show_cart.set()

    else:
        await candidates_prop(state, [await players_prop(state, id_player=id_player, param="nickname") for id_player in await players_condition_prop(state)])
        bunker_keyboard_value = keyboards.set_bunker_value(await candidates_prop(state))
      
        await message.answer("круг завершился \n\n Перейдем к голосованию", reply_markup=keyboards.create_inline(bunker_keyboard_value, type_placement="row"))

        await FSMAdmin.voting.set()

        await voting_prop(state, event="add", type_voting="bunker", id_message=0, variants=["изгнать " + str(player) for player in await candidates_prop(state)])


async def voting_bunker(query: types.CallbackQuery, state: FSMContext):
    id_player = query.from_user.id

    if id_player in await voting_prop(state, event="quantity_players", type_voting="bunker"):  #! 
        await bot.send_message(query.message.chat.id, text="__player__ вы уже проголосовали")
    
    
    else:
        await voting_prop(state, type_voting="bunker", name_variants=query.data, value=id_player)

    bunker_keyboard_value = keyboards.set_bunker_value(await candidates_prop(state))
    await query.message.edit_reply_markup(await change_buttons_message(state, type_voting="bunker", voting_data=bunker_keyboard_value, param_keyboard="row"))

    if len(await voting_prop(state, event="quantity_players", type_voting="bunker")) == len(await candidates_prop(state)):
        winners = [player.split()[-1] for player in await voting_prop(state, event="get_winner", type_voting="bunker")]
        
        if len(winners) > 1:
            await output_result(query, state, type_voting="bunker")

            await candidates_prop(state, winners)
            bunker_keyboard = keyboards.set_bunker_value(await candidates_prop(state))
            await voting_prop(state, event="add", type_voting="bunker", id_message=0, variants=await candidates_prop(state))

            await bot.send_message(chat_id=query.message.chat.id, text="точного результата нет, повторное голосование", reply_markup=bunker_keyboard)

        else:
            await output_result(query, state, type_voting="bunker")
            await candidates_prop(state, value=None)
            await delete_player(state, await get_id_name(state, winners[0][1:]))

            await voting_prop(state, event="del", type_voting="bunker")

            await bot.send_message(chat_id=query.message.chat.id, text=f"{winners[0]} был исключен из бункера")
            await FSMAdmin.n_step.set()


async def get_cart(message: types.Message, state=FSMContext):
    await message.answer(f"вы выбрали карту {message.text}\nвремя на описание карты", reply_markup=keyboards.step_keyboard)
    #! добавить карту в использованные
    await FSMAdmin.voting.set()



async def cancel_handler(message: types.Message, state: FSMContext):

    if message.from_user.id == await admin_id_prop(state):
        await game_over(message, state)
        await message.reply("Игра закончена по просьбе")

        # сбросить ве значения игры   
    else:
        await message.answer("""Игру может закончить администратор {админ}!
        \n Попросите администратора закончить игру или сами станьте администратором""", reply_markup=keyboards.double_inline_keyboard)
        await voting_prop(state, event="add", type_voting="game_over", id_message=0, variants=["да", "нет"])


async def voting_cancel_handler(query: types.CallbackQuery, state=FSMContext):
    id_player = query.from_user.id

    if id_player in await voting_prop(state, event="quantity_players", type_voting="game_over"):
        await bot.send_message(query.message.chat.id, text="__player__ вы уже проголосовали")
    
    
    else:
        await voting_prop(state, type_voting="game_over", name_variants=query.data, value=id_player)

    await query.message.edit_reply_markup(await change_buttons_message(state, type_voting="game_over", voting_data=keyboards.double_inline_value, param_keyboard="add"))

    if len(await voting_prop(state, event="quantity_players", type_voting="game_over")) == len(await players_condition_prop(state)):
        winners = await voting_prop(state, event="get_winner", type_voting="game_over")
        
        if len(winners) > 1:
            await bot.send_message(chat_id=query.message.chat.id, text="точного результата нет")

        else:

            if winners[0] == "да":
                await bot.send_message(chat_id=query.message.chat.id, text="вы решили закончить игру __голосовавшие__")
                await output_result(query, state, type_voting="game_over")
                await game_over(query, state)

            else:
                await bot.send_message(chat_id=query.message.chat.id, text="вы решили продолжить игру __голосовавшие__")
                await output_result(query, state, type_voting="game_over")

                await voting_prop(state, event="del", type_voting="game_over")

        return 
    

async def game_over(message, state: FSMAdmin):
    current_state = await state.get_state()

    if current_state is None:
        return
    
    await state.finish()
        

#* (II) - хендлеры для работы с пользователем, как с объектом 

#! добавление игроков 
async def append_player(message: types.Message, state=FSMContext):  # +-
    id_player = message.from_user.id

    if any(id_player == player for player in await players_condition_prop(state)):

        await message.reply("{игрок}, Вы уже участвуете!", reply_markup=keyboards.player_keyboards)

    # написать код ошибки, если игрок не написал боту

    else:  # -
        await players_prop(state, event="add", id_player=id_player, value={"nickname": message.from_user.username, "card": all_cards.copy()})

        await players_condition_prop(state, id_player=id_player, event="add")

        await bot.send_message(message.chat.id, text="{игрок}, Вы теперь в игре!\nЕсли вы получили это сообщение, то все хорошо!", reply_markup=keyboards.player_keyboards)



#! /выйти
async def leave_player(message: types.Message, state=FSMContext):
    id_player = message.from_user.id

    if any(id_player == player for player in await players_condition_prop(state)):
        print("игрок есть")
        await players_prop(state, event="del", id_player=id_player)
        await players_condition_prop(state, event="del", id_player=id_player)

        await message.reply(f"__игрок__, Вы вышли из игры.\nВсего игроков {len(await players_condition_prop(state))}")

    else:
        await message.reply("__имя__, Вы не участвовали")



async def exclude_player(message: types.Message, state: FSMContext):
    id_player = await get_id_name(state, name=await find_username(message.text))
    if id_player in await players_condition_prop(state):
        if message.from_user.id == await admin_id_prop(state):
            await delete_player(state, id_player)
            await message.reply("__player__ был исключен из игры по просьбе администратора")  

        else:
            await voting_prop(state, event="add", id_message=0, type_voting="player", variants=["исключить игрока", "оставить игрока"])
            await message.reply("Исключить __игрока__ по голосованию", reply_markup=keyboards.expel_player_keyboard)
            async with state.proxy() as data:
                data["fast_data"] = id_player


    else:
        await message.reply("игрока с именем __nickname__ нет")



async def voting_exclude_player(query: types.CallbackQuery, state=FSMContext):
    id_player = query.from_user.id

    if id_player in await voting_prop(state, event="quantity_players", type_voting="player"):
        await bot.send_message(query.message.chat.id, text="__player__ вы уже проголосовали")

    else:
            
        await voting_prop(state, type_voting="player", name_variants=query.data, value=id_player)

    await query.message.edit_reply_markup(await change_buttons_message(state, type_voting="player", voting_data=keyboards.expel_player_value, param_keyboard="add"))


    if len(await voting_prop(state, event="quantity_players", type_voting="player")) == len(await players_condition_prop(state)):
        winners = await voting_prop(state, event="get_winner", type_voting="player")
        
        if len(winners) > 1:
            await bot.send_message(chat_id=query.message.chat.id, text="точного результата нет")

        else:

            if winners[0] == "исключить игрока":
                await output_result(query, state, type_voting="player")

                await bot.send_message(chat_id=query.message.chat.id, text="вы решили исключить игрока __голосовавшие__")

                async with state.proxy() as data:
                    id_ex_player = data["fast_data"] 
                    del data["fast_data"]

                await delete_player(state, id_player=id_ex_player)


            else:
                await output_result(query, state, type_voting="player")

                await bot.send_message(chat_id=query.message.chat.id, text="вы решили не исключать игрока __голосовавшие__")
            
            await voting_prop(state, event="del", type_voting="player")

        return 




#* (III) - хендлеры длс работы пользователя с программой, для получения информации 


#! help
async def get_help(message: types.Message, state=FSMContext):
    await message.reply("***доки*** для игры")


#! /кто играет
async def get_players(message: types.Message, state=FSMContext):
    mes = "\n".join([f"{num + 1} - {player}" for num, player in enumerate(await players_condition_prop(state))])
    await message.reply(f"Всего участников {len(await players_condition_prop(state))}\n\n{mes}")


async def change_admin(message: types.Message, state=FSMContext):
        players = [await players_prop(state, id_player=id_player, param="nickname") for id_player in await players_condition_prop(state)]
        admin_keyboard_value = keyboards.set_admin_value(players)
        print(admin_keyboard_value, " - fisrt")
      
        await message.answer("выберете администратора\n\nголосование", reply_markup=keyboards.create_inline(admin_keyboard_value, type_placement="row"))

        await voting_prop(state, event="add", type_voting="admin", id_message=0, variants=["админ " + str(player) for player in players])


async def voting_change_admin(query: types.CallbackQuery, state: FSMContext):
    id_player = query.from_user.id

    if id_player in await voting_prop(state, event="quantity_players", type_voting="admin"):  #! 
        await bot.send_message(query.message.chat.id, text="__player__ вы уже проголосовали")
    
    else:
        await voting_prop(state, type_voting="admin", name_variants=query.data, value=id_player)

    admin_keyboard_value = keyboards.set_admin_value([await players_prop(state, id_player=id_player, param="nickname") for id_player in await players_condition_prop(state)])
    await query.message.edit_reply_markup(await change_buttons_message(state, type_voting="admin", voting_data=admin_keyboard_value, param_keyboard="row"))


    if len(await voting_prop(state, event="quantity_players", type_voting="admin")) == len(await players_condition_prop(state)):
        winners = [player.split()[-1] for player in await voting_prop(state, event="get_winner", type_voting="admin")]
        
        if len(winners) > 1:
            await output_result(query, state, type_voting="admin")
            await voting_prop(state, event="del", type_voting="admin")
            await bot.send_message(chat_id=query.message.chat.id, text="точного результата нет __admin__ остается администратором")
        else:
            await output_result(query, state, type_voting="admin")
            if await get_id_name(state, winners[0][1:]) == await admin_id_prop(state):
                await bot.send_message(chat_id=query.message.chat.id, text=f"{winners[0]} остается администратором")
            else:
                await voting_prop(state, event="del", type_voting="admin")
                await bot.send_message(chat_id=query.message.chat.id, text=f"{winners[0]} стал новым администратором")

#* (IV) - методы


async def output_result(query: types.CallbackQuery, state: FSMContext, type_voting: str):
    text = await get_result_voting(state, type_voting=type_voting)
    print(text)
    await query.message.edit_text(text)


async def delete_player(state, id_player: int) -> None:
    await players_condition_prop(state, id_player=id_player, event="del")
    await players_prop(state, id_player=id_player, event="del")


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
    dp.register_callback_query_handler(voting_bunker, lambda answer: "изгнать" in answer.data, state=FSMAdmin)
    dp.register_message_handler(get_cart, commands=["cart"], state=FSMAdmin)

    dp.register_message_handler(cancel_handler, commands=["stop"], state="*")
    dp.register_callback_query_handler(voting_cancel_handler, lambda answer: answer.data in ("да", "нет"), state=FSMAdmin)

    dp.register_message_handler(append_player, commands=["i"], state="*")
    dp.register_message_handler(change_admin, commands=["admin"], state=FSMAdmin)
    dp.register_callback_query_handler(voting_change_admin, lambda answer: "админ" in answer.data, state=FSMAdmin)

    dp.register_message_handler(leave_player, commands=["выйти", "leave"], state="*")
    dp.register_message_handler(exclude_player, commands=["изгнать"], state="*")
    dp.register_callback_query_handler(voting_exclude_player, lambda answer: answer.data in ("исключить игрока", "оставить игрока"), state=FSMAdmin)

    dp.register_message_handler(get_help, commands=["help"], state="*")
    dp.register_message_handler(get_players, commands=["кто", "who"], state="*")
    