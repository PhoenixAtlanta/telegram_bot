from random import shuffle

from app import bot 
from working_data.working_json import *



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

        if not id_player:
            id_player = await get_player(state)

        if event is None:  # вернуть значение по ключу
            return data["players"][id_player][key]
        
        elif key == "card":  # удалить карту из списка
            cards = data["players"][id_player][key]
            cards.remove(value)
            data["players"][id_player][key] = cards
        
        elif event == "key":  # изменить элемент
            data["players"][id_player][key] = value

        elif event == "add":  # добавить игрока
            data["players"][id_player] = {"nickname": value["nickname"], "card": value["card"]}

        elif event == "del":  # удалить игрока
            keys = list(data["players"].keys())
            keys.remove(id_player)
            new_dict = {}

            for key in keys:
                new_dict[keys] = data["players"][keys]

            data["players"] = new_dict.copy()
            del new_dict
        

async def step_player_prop(state, event=None):
    """получить или установить новое значение следующего игрока"""

    async with state.proxy() as data:
        if event is None:
            return data["step_player"]

        elif event == "1":
            data["step_player"] += 1

        elif event == "0":
            data["step_player"] = 0


async def step_prop(state, event=None):
    """получить номер хода или увеличить его"""
    async with state.proxy() as data:
        if event is None:
            return data["step"]
        
        elif event == "1":
            data["step"] += 1


async def player_condition_prop(state, id_player: int=0, event=None):  # получить список игроков или изменить его 
    """получить список игроков или изменить его"""
    async with state.proxy() as data:
        if event is None:
            return data["players_condition"]
        
        elif event == "add":
            data["players_condition"].append(id_player)

        elif event == "del":
            data["players_condition"].remove(id_player)


async def get_player(state):  # получить id текущего игрока  
    """получить id текущего игрока"""
    async with state.proxy() as data:
        print(data["players_condition"][await step_player_prop(state)])
        return data["players_condition"][await step_player_prop(state)]
    

async def shuffle_players(state):  # изменить последовательность
    """поменять порядок игроков"""
    async with state.proxy() as data:
        shuffle(data["players_condition"])


async def voting_prop(state, type_voting: str, chat_id=None, voting_params: dict={}, event: str="get"):
    """--"""
    async with state.proxy() as data:
        if event == "get":
            return data["voting"][type_voting]
        
        elif event == "add":    
            voting = await bot.send_poll(chat_id, question=voting_params["topic"], options=voting_params["variants"] + ["second"], is_anonymous=voting_params["is_anonymous"], type=voting_params["type"])
            data["voting"][type_voting] = voting

        elif event == "del":
            data["voting"][type_voting] = None


async def close_voting(state, message, type_voting: str):
    """---"""
    async with state.proxy() as data:
        quiz = data["voting"][type_voting]
        answer = await bot.stop_poll(message.chat.id, message_id=quiz.message_id)
        return answer


async def get_chat_id(state):
    async with state.proxy() as data:
        return data["chat_id"]


async def voting_result(voting_result, response_type="all"):
    players_name = sorted(voting_result["options"], key=lambda x: x["voter_count"])
    players_name = list(filter(lambda x: x["voter_count"] == players_name[-1]["voter_count"], players_name))

    if response_type == "all":
        return players_name
    
    elif response_type == "text":
        return [elem["text"] for elem in players_name]
    
    elif response_type == "count":
        return [elem["voter_count"] for elem in players_name]


async def last_message(state, message=None, event="set"):
    async with state.proxy() as data:
        if event == "get":
            return data["last_message"]

        elif event == "set":
            data["last_message"] = message


async def get_id_name(state, name):
    async with state.proxy() as data:
        for id_player in data["players"]:
            if data["players"][id_player]["nickname"] == name:
                return id_player
            

async def update_chat_data(id_chat: int, new_data):
    try:
        data = await read_json()
        print(1)
        data["chat_data"][id_chat] = new_data
        print(2)
        await write_data(data)
        print(3)
    except Exception as e:
        print(e)

