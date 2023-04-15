from random import shuffle



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

        print(id_player)

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
