from random import shuffle, choice

import keyboards
from params import nickname_symbols, worlds_joining_game


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


async def players_condition_prop(state, nickname: int=None, event: str=None):  # получить список игроков или изменить его 
    """получить список игроков или изменить его"""
    async with state.proxy() as data:

        if event is None:
            return data["players_condition"]
    
        elif event == "add":
            data["players_condition"] = (data["players_condition"] if "players_condition" in data.keys() else []) + [nickname]

        elif event == "del":
            data["players_condition"].remove(nickname)


async def players_prop(state, nickname: int=None, param: str=None, value=None, event=None, cart: list=None):
    """получить данные игрока или записать"""
    async with state.proxy() as data:
        if nickname is None:
            nickname = await get_player(state)

        if event is None:  # получить данные
            return data["players"][nickname][param]
            
        elif event == "add":
            if "players" not in data.keys():
                data["players"] = {}

            data["players"][nickname] = {"nickname": nickname, "cart": cart}

  
        elif event == "del":
            if param is None:
                keys = list(data["players"].keys())
                keys.remove(nickname)
                new_dict = {}

                for key in keys:
                    new_dict[key] = data["players"][key]

                data["players"] = new_dict.copy()
                del new_dict
            elif param == "cart":
                data["players"][nickname]["cart"].remove(value)
                    
        elif value:  # записать данные
            data["players"][nickname][param] = value

        

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
    """получить nickname текущего игрока"""
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
            

async def voting_prop(state, event: str=None, type_voting: str=None, name_variants: str=None, key_variants: str=None,
                      value=None, id_message: int=None, variants: list=[]):
    async with state.proxy() as data:

        if event == "add":
            data["voting"][type_voting] = {"id_message": id_message, "quantity_players": [], "variants": {}}

            for variant in variants:
                elem = {"number": 0, "choices": []}
                data["voting"][type_voting]["variants"][variant] = elem

        elif event == "del":
            data["voting"][type_voting] = {}

        elif name_variants:  # проголосовали
            data["voting"][type_voting]["variants"][name_variants]["choices"].append(value)
            data["voting"][type_voting]["variants"][name_variants]["number"] += 1
            data["voting"][type_voting]["quantity_players"].append(value)


        elif event == "get_winner":
            winners = {key: data["voting"][type_voting]["variants"][key] for key in sorted(data["voting"][type_voting]["variants"],
                                                                                            key=lambda key: data["voting"][type_voting]["variants"][key]["number"], reverse=True)}
            
            winners = list(filter(lambda key: winners[list(winners.keys())[0]]["number"] == winners[key]["number"], winners))

            
            return winners

         
        elif event == "number":
            return data["voting"][type_voting]["variants"][name_variants]["number"]
                 
        elif event == "choice":
            return data["voting"][type_voting]["variants"][name_variants]["choices"]
               
        elif event == "quantity_players":
            if value:
                data["voting"][type_voting]["quantity_players"].append(value)

            else:
                return data["voting"][type_voting]["quantity_players"]
                 
        elif event == "id_message":
            return data["voting"][type_voting]["id_message"]
        
        
async def change_buttons_message(state, voting_data: dict, type_voting: str, param_keyboard: str="add"):
    async with state.proxy() as data:
        result_now = {key: data["voting"][type_voting]["variants"][key]["number"] for key in data["voting"][type_voting]["variants"]}

    for key in result_now:
        voting_data[key]["number"] = result_now[key] 

    inline_button = {key: voting_data[key] for key in result_now} 
    return keyboards.create_inline(inline_button, type_placement=param_keyboard)


async def get_result_voting(state, type_voting):

    async with state.proxy() as data:

        result = {key: data["voting"][type_voting]['variants'][key] for key in data["voting"][type_voting]['variants']}
        for key in result:
            result[key]["choices"] = [await players_prop(state, nickname=id_player, param="nickname") for id_player in result[key]["choices"]]  


        quantity_str =  {elem: "\n".join(result[elem]["choices"]) for elem in result}

        str_result = "Результаты голосования:\n\n" + "\n".join([f"{elem} - {result[elem]['number']}\n   {quantity_str[elem]}" for elem in result])
    return str_result


async def candidates_prop(state, value: list=None):
    async with state.proxy() as data:
        if value is None:
            return data["candidates"]

        data["candidates"] = value


def find_all_usernames(text) -> str:
    start = False
    all_usernames = []
    username = ""

    for letter in text + ".":

        if letter in nickname_symbols and start:
            username += letter

        else:
            start = False
            if username:
                all_usernames.append("@" + username)
                username = ""

            if letter == "@":
                start = True
    
    return all_usernames


def get_world_start() -> str:
    world = choice(worlds_joining_game)

    return world


async def start_word(state) -> str:
    async with state.proxy() as data:
        return data["start_word"]


def create_dialog(text: str, value) -> str:
    index_value = 0
    dialog_message = ""

    for i, elem in enumerate(text):
        if elem == "?":
            dialog_message += value[index_value]
            index_value += 1

            if index_value == len(value):
                dialog_message += text[i + 1:-1]
        else:
            dialog_message += elem

    return dialog_message


async def print_state(state, key="voting"):
    async with state.proxy() as data:
        print(data)
