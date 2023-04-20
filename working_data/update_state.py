from random import shuffle

from app import bot 
from working_data.working_json import *


async def admin_id_prop(state, value: int=None):
    """получить id админа или установить новое"""
    async with state.proxy() as data:

        if value is None:
            return data["admin_id"]
        
        else:
            data["admin_id"] = value




async def chat_id_prop(state, value: int=None):
    """работа с id чата"""
    async with state.proxy() as data:
        if value is None:
            return data["chat_id"]
        
        else:
            data["chat_id"] = value




async def players_condition_prop(state, id_player: int=None, event: str=None):  # получить список игроков или изменить его 
    """получить список игроков или изменить его"""
    async with state.proxy() as data:


        if event is None:
            return data["players_condition"]
        
        elif event == "add":

            data["players_condition"] = (data["players_condition"] if "players_condition" in data.keys() else []) + [id_player]

        elif event == "del":
            data["players_condition"].remove(id_player)




async def players_prop(state, id_player: int=None, param: str=None, value=None, event=None, nickname: str=None, card: list=None):
    """получить данные игрока или записать"""
    async with state.proxy() as data:
        if id_player is None:
            id_player = await get_player(state)
        

        if event is None:  # получить данные
            if param is None:
                return data["players"][id_player]
            
            else:
                return data["players"][id_player][param]
            
        elif event == "add":
            if "players" not in data.keys():
                data["players"] = {}
                print(3)

            data["players"][id_player] = {"nickname": nickname, "card": card}

  
        elif event == "del":  # удалить игрока
            if param is None:

                keys = list(data["players"].keys())
                keys.remove(id_player)
                new_dict = {}

                for key in keys:
                    new_dict[keys] = data["players"][key]

                data["players"] = new_dict.copy()
                del new_dict
            
            elif param == "card":
                data["players"][id_player]["card"].remove(value)
                    
        elif value:  # записать данные
            data["players"][id_player][param] = value

        

async def current_player_prop(state, value=None):
    """получить или установить новое значение следующего игрока"""

    async with state.proxy() as data:
        if value is None:
            return data["current_player"]

        else:
            data["current_player"] = value


async def number_step_prop(state, value=None):
    """получить номер хода или увеличить его"""
    async with state.proxy() as data:
        if value is None:
            return data["number_step"]
        
        else:
            if "number_step" not in data.keys():
                data["number_step"] = 0

            data["number_step"] += value


async def voting(state):
    ...


async def get_player(state):  # получить id текущего игрока  
    """получить id текущего игрока"""
    async with state.proxy() as data:
        return data["players_condition"][await current_player_prop(state)]
    

async def shuffle_players(state):  # изменить последовательность
    """поменять порядок игроков"""
    async with state.proxy() as data:
        shuffle(data["players_condition"])


async def get_id_name(state, name):
    async with state.proxy() as data:
        for id_player in data["players"]:
            if data["players"][id_player]["nickname"] == name:
                return id_player
            

    """
voting: {
    bunker: {
        id_message = int,
        variants: {
            name: {
                id: int,
                number: int,
                choices: list[id,]
            }
        }
    }
}
    """


async def voting_get(state, event: str=None, type_voting: str=None, name_variants: str=None, key_variants: str=None,
                      value=None, id_message: int=None, variants: list=[]):
    async with state.proxy() as data:

        if event == "add":
            data["voting"][type_voting] = {"id_message": id_message, "variants": {}}

            for variant in variants:
                elem = {"number": 0, "choices": []}
                data["voting"][type_voting]["variants"][variant] = elem

        elif event == "del":
            data["voting"][type_voting] = {}

        elif name_variants:  # проголосовали
            data["voting"][type_voting]["variants"][name_variants]["choice"].append(value)
            data["voting"][type_voting]["variants"][name_variants]["number"] += 1

        elif event == "number":
            return data["voting"][type_voting]["variants"][name_variants]["number"]
        
        elif event == "choices":
            data["voting"][type_voting]["variants"][name_variants]["choice"].append(value)

        elif event == "id_message":
            return data["voting"][type_voting]["id_message"]
