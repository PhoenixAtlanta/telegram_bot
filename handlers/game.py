from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.types.chat_member import ChatMemberMember 
from aiogram.dispatcher import filters
from aiogram import types, Dispatcher
from aiogram.types import InputFile, chat_member


from app import bot, data_base
from working_data import *
import keyboards
from params import all_carts, cart_for_game

class FSMAdmin(StatesGroup):  # машина состояния
    team_formation = State()  # образование команды
    next_player = State()
    n_step = State()  # шаг игры
    show_cart = State()  # пользователь показывает одну из карт
    voting = State()  # голосование 
    stop = State()  # завершение игры


#* (I) - хендлеры управления игрой 

async def cmd_start_game(message: types.Message, state=FSMContext):
    try:
        await FSMAdmin.team_formation.set()
        username = "@" + message.from_user.username


        async with state.proxy() as data:
            data["current_player"]: int=0
            data["start_word"]: str=get_world_start()
            data["number_step"]: int=1
            data["admin_id"]: int=message.from_user.username
            data["chat_id"]: int=message.chat.id
            data["players_condition"]: list=[username, ]
            data["candidates"]: list=[]
            data["players"]: dict={username: {"cart": cart_for_game.copy()}}
            data["voting"]: dict={
                                    "bunker": {},  # сделать метод, который будет создавать пустой шаблон
                                    "admin": {},
                                    "player": {},
                                    "game_over": {}
                                    }
            
        await message.reply(create_dialog(dialog("start_play"),
                                                value=[username, await start_word(state)]), reply_markup=keyboards.start_keyboard)
    except Exception as e:
        print(e)


#! /go
async def go(message: types.Message, state=FSMContext): # +
    await FSMAdmin.n_step.set()

    await message.reply("Игра началась!")
    image_disaster_data = data_base.get_data_image("Катастрофа")
    photo_disaster = InputFile(image_disaster_data["path_to_image"])

    await message.answer("Игра началась! Катастрофа, которая произошла в мире.", reply_markup=types.ReplyKeyboardRemove())
    await bot.send_photo(chat_id=message.chat.id, photo=photo_disaster)
    await message.answer(f"{image_disaster_data['description'].split(';')[1]}\n\n{image_disaster_data['description'].split(';')[-1]}")
    
    await shuffle_players(state)
    
    await message.answer("Для того чтобы получить карты характеристики? напишите боту(@BunkerGameBot_bot) /cart!")
    await next_step(message, state)


async def next_step(message: types.Message, state=FSMContext):
    if await number_step_prop(state) == 5 or len(await players_condition_prop(state)) == 1: 
        winners = "/n- ".join(await players_condition_prop(state))
        message.answer(f"Игра закончена! Все кто остались в бункере победили!/n- {winners}")
        await game_over(message, state)


    if await current_player_prop(state) <= len(await players_condition_prop(state)) - 1:

        nickname = await get_player(state)
        await message.answer(f"Ход игрока {nickname}!")

        if await number_step_prop(state) > 1:
            all_cart = '\n-'.join(await players_prop(state, nickname=nickname, param='cart'))
            await message.answer(f"{nickname}. Выберете одну из карт:\n-{all_cart}")

        else:
            await message.answer(f"{nickname}. Откройте карту - Профессия", reply_markup=keyboards.profession_keyboard)

        await FSMAdmin.show_cart.set()

    else:
        if await number_step_prop(state) > 1:
            await message.answer("Круг завершился!\n\nНастало время решить, кто не достоин находиться в бункере.\nВыгнать игрока можно по команде /delete @(username)", reply_markup=keyboards.player_keyboards)
            await FSMAdmin.voting.set()
        else:
            await last_player(message, state)
            await next_step(message, state)


async def voting_bunker(message: types.Message, state: FSMAdmin):
    nickname = find_all_usernames(message.text)[0]

    await last_player(message, state)
    await delete_player(message, state, nickname)


async def get_cart(message: types.Message, state=FSMContext):
    try:
        nickname = await get_player(state)
        cart = message.text 
        await players_prop(state, event="del", param="cart", nickname=nickname, value=cart)
        await message.reply(f"{nickname} выбрал карту - {cart}, пропишите команду /all по завершению", reply_markup=keyboards.player_keyboards)

        await FSMAdmin.next_player.set()
    except Exception as e:
        print(e)


async def next_player(message: types.Message, state=FSMContext):
    await current_player_prop(state, value=await current_player_prop(state) + 1)

    await FSMAdmin.n_step.set()
    await next_step(message, state)


async def cancel_handler(message: types.Message, state: FSMContext):

    if message.from_user.id == await admin_id_prop(state):
        await game_over(message, state)
        await message.reply("Игра закончена по просьбе")

        # сбросить ве значения игры   
    else:
        await message.answer("""Игру может закончить администратор {админ}!
        \n Попросите администратора закончить игру или сами станьте администратором""", reply_markup=keyboards.double_inline_keyboard)
        await voting_prop(state, event="add", type_voting="game_over", id_message=0, variants=["да", "нет"])

    

async def game_over(message: types.Message, state: FSMAdmin):
    current_state = await state.get_state()
    message.answer(text="До скорого!", reply_markup=types.ReplyKeyboardRemove())

    if current_state is None:
        return
    
    await state.finish()
        

#* (II) - хендлеры для работы с пользователем, как с объектом 

async def append_player(message: types.Message, state=FSMContext): # +
    players = find_all_usernames(message.text)

    for player in players:
        if player in await players_condition_prop(state):
            await message.reply(f"Игрок {player} уже играет")
        else:
            await message.reply(f"Игрок {player} добавлен")

            await players_prop(state, event="add", nickname=player, cart=cart_for_game.copy())
            await players_condition_prop(state, nickname=player, event="add")


#! /выйти
async def leave_player(message: types.Message, state=FSMContext):
    id_player = message.from_user.id

    if any(id_player == player for player in await players_condition_prop(state)):
        print("игрок есть")
        await players_prop(state, event="del", nickname=id_player)
        await players_condition_prop(state, event="del", nickname=id_player)

        await message.reply(f"__игрок__, Вы вышли из игры.\nВсего игроков {len(await players_condition_prop(state))}")

    else:
        await message.reply("__имя__, Вы не участвовали")



async def exclude_player(message: types.Message, state: FSMContext):
    id_player = await get_id_name(state, name=await find_all_usernames(message.text)[0])
    if id_player in await players_condition_prop(state):
        if message.from_user.id == await admin_id_prop(state):
            await delete_player(message, state, id_player)
            await message.reply("__player__ был исключен из игры по просьбе администратора")  

        else:
            await voting_prop(state, event="add", id_message=0, type_voting="player", variants=["исключить игрока", "оставить игрока"])
            await message.reply("Исключить __игрока__ по голосованию", reply_markup=keyboards.expel_player_keyboard)
            async with state.proxy() as data:
                data["fast_data"] = id_player


    else:
        await message.reply("игрока с именем __nickname__ нет")




#* (III) - хендлеры длс работы пользователя с программой, для получения информации 


#! help
async def get_help(message: types.Message, state=FSMContext):
    await message.reply("***доки*** для игры")


#! /кто играет
async def get_players(message: types.Message, state=FSMContext):
    mes = "\n".join([f"{num + 1} - {player}" for num, player in enumerate(await players_condition_prop(state))])
    await message.reply(f"Всего участников {len(await players_condition_prop(state))}\n\n{mes}")

#* (IV) - методы

async def get_now_player(message: types.Message, state=FSMContext):
    await message.reply(f"Сейчас ходит {await get_player(state)}")


async def delete_player(message: types.Message, state, nickname: str) -> None:
    await players_condition_prop(state, nickname=nickname, event="del")
    await players_prop(state, nickname=nickname, event="del")
    await message.reply(f"Игрок {nickname} исключен из бункера.")

    await FSMAdmin.n_step.set()
    await next_step(message, state)


async def last_player(message: types.Message, state: FSMContext):
    await number_step_prop(state, value=1)
    await current_player_prop(state, value=0)


async def generate_cart(message: types.Message):
        if message.chat.type == "private":
            id_player = message.from_user.id
            for type_cart in all_carts:
                if type_cart != "Катастрофа":
                    image_data = data_base.get_data_image(type_cart)
                    photo = InputFile(image_data["path_to_image"])

                    await bot.send_photo(chat_id=id_player, photo=photo)
                    await bot.send_message(chat_id=id_player, text=f"Тип карты:\n{image_data['description'].split(';')[0]}\n\nНазвание карты:\n{image_data['description'].split(';')[1]}\n\nОписание:\n{image_data['description'].split(';')[-1]}")
        else:
            await message.reply("Бот раздает карты только в личных сообщения.")


def register_handler_game(dp: Dispatcher):
    dp.register_message_handler(cmd_start_game, commands=["start"])
    dp.register_message_handler(go, commands=["go"], state=FSMAdmin.team_formation)
    dp.register_message_handler(next_step, commands=["next_step"], state=FSMAdmin.n_step)
    dp.register_message_handler(next_player, commands=["all"], state=FSMAdmin.next_player)

    dp.register_message_handler(voting_bunker, filters.Text(contains="/delete"))
    dp.register_message_handler(get_cart, filters.Text(equals=cart_for_game), state=FSMAdmin.show_cart)

    dp.register_message_handler(cancel_handler, commands=["stop"], state="*")

    dp.register_message_handler(append_player, filters.Text(contains="/append"), state=FSMAdmin.team_formation)
  
    dp.register_message_handler(get_help, commands=["help"], state="*")
    dp.register_message_handler(get_now_player, commands=["now"], state="*")
    dp.register_message_handler(get_players, commands=["players"], state="*")
    dp.register_message_handler(generate_cart, commands=["cart"], state="*")
    
    