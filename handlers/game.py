from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import filters
from aiogram import types, Dispatcher
from aiogram.types import InputFile, ReplyKeyboardRemove

from app import bot, json_data_base, params_game
from data import json_data_work, state_data_work
import keyboards


MAX_STEP = 5  # количество кругов 
MIN_PLAYER = 2  # минимальное количество игроков 

# класс состояния fsm машины
class FSMAdmin(StatesGroup):  # машина состояния
    team_formation = State()  # образование команды
    next_player = State()
    n_step = State()  # шаг игры
    show_cart = State()  # пользователь показывает одну из карт
    voting = State()  # голосование 
    stop = State()  # завершение игры


#* (I) - хендлеры управления игрой 
# хендлер, который отвечает за старт игры, создание бд машины
async def cmd_start_game(message: types.Message, state=FSMContext):
    await FSMAdmin.team_formation.set()  # установить значение машины, в формирование команды 
    username = "@" + message.from_user.username  # получить username

    async with state.proxy() as data: 
        data["current_player"]: int=0  # индекс игрока, который ходит
        data["number_step"]: int=3  # номер круга игры
        data["admin_id"]: int=username
        data["chat_id"]: int=message.chat.id
        data["players_condition"]: list=[username, ]  # игроки которые участвуют
        # список карт, который пользователь еще не использовал 
        data["players"]: dict={username: {"cart": params_game.cart_for_game}}  
 
    # оповестить всех, что игра началась, и идет набор команды 
    await message.reply(state_data_work.create_dialog(
        json_data_work.dialog("start_play"), value=[username]),
        reply_markup=keyboards.go_start_keyboard)


# оповещение, что игра началась, генерация карт
async def go(message: types.Message, state=FSMContext):
    await FSMAdmin.n_step.set()  # состояние машины "следующий ход"

    await message.reply("Игра началась!", reply_markup=ReplyKeyboardRemove())
    image_disaster_data = json_data_base.get_random_cart("Катастрофа")
    # загрузка картинки "катастрофа"
    photo_disaster = InputFile(image_disaster_data["path_to_image"])  

    await message.answer(f"""Игра началась! Катастрофа, которая произошла в мире
{image_disaster_data['name'].upper()}""")
    
    # отправить фото карты и описание
    await bot.send_photo(chat_id=message.chat.id, photo=photo_disaster)  
    await message.answer(f"""{image_disaster_data['description'].split(';')[1]}
    \n{image_disaster_data['description'].split(';')[-1]}""")  
    
    await state_data_work.shuffle_players(state)  # перемешать последовательность игроков
    await message.answer("""Для того чтобы получить Ваши карты характеристики, 
напишите боту @BunkerGameBot_bot - /carts!""")
    await next_step(message, state)



async def next_step(message: types.Message, state=FSMContext):
    # проверка на логический конец игры, или это последний круг или игроков меньше 3
    if await state_data_work.number_step_prop(state) == MAX_STEP or \
        len(await state_data_work.players_condition_prop(state)) <= MIN_PLAYER: 

        winners = "\n- ".join(await state_data_work.players_condition_prop(state))
        await message.answer(
            f"Игра закончена! Все кто остались в бункере победили!\n- {winners}")
        await game_over(message, state)

    # если это был не последний игрок в кругу
    if await state_data_work.current_player_prop(state) <= len(
        await state_data_work.players_condition_prop(state)) - 1:

        nickname = await state_data_work.get_player(state)
        await message.answer(f"Ход игрока {nickname}!")
        # если это не первый круг
        if await state_data_work.number_step_prop(state) > 1:
            # карты которые игрок еще не использовал
            all_carts = await state_data_work.players_prop(
                state, nickname=nickname, param='cart')
            all_carts_text = '\n-'.join(all_carts)
            await message.answer(f"{nickname}. Выберете одну из карт:\n-{all_carts_text}", 
                                reply_markup=keyboards.create_carts_buttons(all_carts))
            
        else:
            await message.answer(f"{nickname}. Откройте карту - Профессия", 
                                reply_markup=keyboards.profession_keyboard)
            
        await FSMAdmin.show_cart.set()  # установить машину на "показать карту"


    else:  # реализовать голосование
        # если это не первый круг (правила игры)
        if await state_data_work.number_step_prop(state) > 1:  
            await message.answer(json_data_work.dialog("voting_text"),
                                reply_markup=ReplyKeyboardRemove())
            await FSMAdmin.voting.set()  # установить машину на "голосование"

        else:
            await update_circle(message, state)  # сбросить круг
            await next_step(message, state)  # следующий ход



# удалить игрока по голосованию
async def voting_bunker(message: types.Message, state: FSMAdmin):
    await update_circle(message, state)  # следующий круг
    await delete_player(message, state, 
                        send_msg="Игрока, ? выгнали из бункера по итогам голосования")
    await FSMAdmin.n_step.set()  # поставить состояние машины на "следующий ход"
    await next_step(message, state)  # запустить функцию следующего хода  


# принимает какую карту выбрал игрок 
async def get_cart(message: types.Message, state=FSMContext):
    nickname = await state_data_work.get_player(state)  # ник игрока который ходит 
    cart = message.text.split()[0]  # получить название карты
    # проверить использовал ли пользователь раньше эту карту 
    if cart in await state_data_work.players_prop(state, nickname=nickname, param="cart"):
        # отметить что карты была использована 
        await state_data_work.players_prop(state, event="del", param="cart",
                                        nickname=nickname, value=cart)
        await message.reply(f"""{nickname} выбрал карту - {cart},
    пропишите команду /all по завершению""", reply_markup=keyboards.all_step_keyboard)
        await FSMAdmin.next_player.set()  # ожидание, пока пользователь не напишет /all

    else:
        await message.reply(f"""{nickname}, Вы уже использовали эту карту ({cart}),
используйте другую!""")


async def next_player(message: types.Message, state=FSMContext):
    # увеличить ход игроков
    nickname = await state_data_work.get_player(state)
    await message.reply(f"{nickname} закончил свой ход.")
    # увеличить индекс игрока
    await state_data_work.current_player_prop(
        state, value=await state_data_work.current_player_prop(state) + 1)
    await FSMAdmin.n_step.set()  # следующий ход
    await next_step(message, state)


# закончить игру, если игрок, который попросил - администратор
async def cancel_handler(message: types.Message, state: FSMContext):
    if "@" + message.from_user.username == await state_data_work.admin_id_prop(state):
        await message.reply("Игра закончена по просьбе")
        await game_over(message, state)


async def game_over(message: types.Message, state: FSMAdmin):
    current_state = await state.get_state()
    await message.answer(text="До скорого!", reply_markup=types.ReplyKeyboardRemove())

    if current_state is None:
        return
    
    await state.finish()
        

#* (II) - хендлеры для работы с пользователем, как с объектом 
# добавление игроков при помощи сообщения
async def append_player(message: types.Message, state=FSMContext):
    players = state_data_work.find_all_usernames(message.text)  # найти игроков, в сообщении по @

    for player in players:
        if player in await state_data_work.players_condition_prop(state):
            await message.reply(f"Игрок {player} уже играет")

        else:
            await message.reply(f"Игрок, {player} добавлен")
            await state_data_work.players_prop(state, event="add", nickname=player,
                                               cart=params_game.cart_for_game.copy())
            await state_data_work.players_condition_prop(state, nickname=player, event="add")


# удалить игрока при помощи команды
async def cmd_delete_player(message: types.Message, state: FSMContext):
    await delete_player(message, state)



#* (III) - хендлеры длс работы пользователя с программой, для получения информации 
#! help
async def get_help(message: types.Message, state=FSMContext):
    await message.reply(json_data_work.dialog("help_admin"))


# узнать всех игроков, которые играют
async def get_players(message: types.Message, state=FSMContext):
    # получить всех игроков, которые еще не выбыли
    players = await state_data_work.players_condition_prop(state)
    # оформить в виде строки
    mes = "\n".join([f"{num + 1} - {player}" for num, player
                    in enumerate(players)])
    await message.reply(f"""Всего участников {len(players)}\n\n{mes}""")


#* (IV) - методы
# узнать игрока, который сейчас ходит
async def get_now_player(message: types.Message, state=FSMContext):
    if await state.get_state() not in ("FSMAdmin:team_formation", None):
        await message.reply(f"Сейчас ходит {await state_data_work.get_player(state)}")


# удаление игрока
async def delete_player(message: types.Message, state: FSMContext,
                         send_msg: str="Игрок, ? был исключен") -> None:        
    nicknames = state_data_work.find_all_usernames(message.text)  # получить ник игрока
    if not nicknames:
        await message.reply("Имя пользователя не указанно!")
        return 
    nickname = nicknames[0]
    # если он существует
    if nickname in await state_data_work.players_condition_prop(state):
        await state_data_work.players_condition_prop(state, nickname=nickname, event="del")
        await state_data_work.players_prop(state, nickname=nickname, event="del")
        # оповестить, чо игрок удален
        await message.reply(state_data_work.create_dialog(text=send_msg, value=[nickname]))

    else:
        await message.reply(f"Игрока, {nickname} нет в игре.")


async def update_circle(message: types.Message, state: FSMContext):
    await state_data_work.number_step_prop(state, value=1)  # увеличить номер круга на один
    await state_data_work.current_player_prop(state, value=0)  # начать с первого игрока


def register_handler_game(dp: Dispatcher):
    # хендлеры управления игрой
    dp.register_message_handler(cmd_start_game, commands=["start"])
    dp.register_message_handler(go, commands=["go"], state=FSMAdmin.team_formation)
    dp.register_message_handler(append_player, filters.Text(contains="/append"), 
                                state=FSMAdmin.team_formation)
    dp.register_message_handler(voting_bunker, filters.Text(contains="/voting"), 
                                state=FSMAdmin.voting)
    dp.register_message_handler(cmd_delete_player, filters.Text(contains="/delete"), state="*")
    dp.register_message_handler(get_cart, filters.Text(equals=params_game.cart_for_game),
                                state=FSMAdmin.show_cart)
    dp.register_message_handler(next_player, commands=["all"], state=FSMAdmin.next_player)
    dp.register_message_handler(cancel_handler, commands=["stop"], state="*")
    # хендлеры, которые помогают ориентироваться 
    dp.register_message_handler(get_help, commands=["help"], state="*")
    dp.register_message_handler(get_now_player, commands=["now"], state="*")
    dp.register_message_handler(get_players, commands=["players"], state="*")
    