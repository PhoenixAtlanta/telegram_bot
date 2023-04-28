from random import shuffle

from app import params_game


# получить или записать id администратора
async def admin_id_prop(state, value: int = None):
    async with state.proxy() as data:
        if value is None:
            return data["admin_id"]        

        else:
            data["admin_id"] = value


# получить или записать данные чата
async def chat_id_prop(state, value: int = None):
    """работа с id чата"""
    async with state.proxy() as data:
        if value is None:
            return data["chat_id"]

        else:
            data["chat_id"] = value


# работа со списком игроков
async def players_condition_prop(state, nickname: int = None, event: str = None):
    async with state.proxy() as data:
        if event is None:
            return data["players_condition"]

        elif event == "add":  # добавить игрока
            data["players_condition"] = (
                data["players_condition"] if "players_condition" in data.keys() else []
            ) + [nickname]

        elif event == "del":  # удалить игрока
            print(nickname)
            data["players_condition"].remove(nickname)



async def players_prop(state, nickname: int = None, param: str = None,
                        value=None, event=None, cart: list = None,):
    """работа с данными игроков.

    Args:
        state (_type_): данные FSM машины.
        nickname (int, optional): имя, ключ игрока. Defaults to None.
        param (str, optional): значение по ключу, чтобы получить, 
            список карт игрока. Defaults to None.
        value (_type_, optional): значение, которое необходимо записать,
            если в этом есть необходимость. Defaults to None.
        event (_type_, optional): для удаления или добавления данных. Defaults to None.
        cart (list, optional): карты игрока, при добавлении игрока. Defaults to None.

    Returns:
        _type_: возвращает данные игрока.
    """
    async with state.proxy() as data:
        if nickname is None:
            # если имя игрока не известно, значит получить игрока, который ходит
            nickname = await get_player(state)  

        if event is None:  # получить данные по ключу, который храниться в param
            return data["players"][nickname][param]

        elif event == "add":  # добавить игрока
            if "players" not in data.keys():
                data["players"] = {}

            data["players"][nickname] = {"nickname": nickname, "cart": cart}

        elif event == "del":  # удалить, игрока или карту 
            if param is None:  # если ключ None, значит удалить игрока
                keys = list(data["players"].keys())
                keys.remove(nickname)
                new_dict = {}

                for key in keys:
                    new_dict[key] = data["players"][key]

                data["players"] = new_dict.copy()
                del new_dict

            elif param == "cart":  # иначе удалить карту
                data["players"][nickname]["cart"].remove(value)

        elif value:  # задать новые значения
            data["players"][nickname][param] = value


# получить или записать индекс игрока, который ходит
async def current_player_prop(state, value=None):
    async with state.proxy() as data:
        if value is None:  # если значение None, то получить данные, иначе изменить
            return data["current_player"]

        else:
            data["current_player"] = value


# получить номер хода или увеличить его
async def number_step_prop(state, value=None):
    async with state.proxy() as data:
        if value is None:
            return data["number_step"]

        else:
            data["number_step"] += value


# получить id текущего игрока
async def get_player(state):  
    async with state.proxy() as data:
        return data["players_condition"][await current_player_prop(state)]


 # изменить порядок игроков, по которому они будут ходить
async def shuffle_players(state): 
    async with state.proxy() as data:
        shuffle(data["players_condition"])


# найти все username в сообщении
def find_all_usernames(text) -> list:
    start = False  # начать запись username
    all_usernames = []  # все найденные username
    username = ""  # создаваемый username

    # перебирает буквы сообщения, "." служит как знак окончания сообщения
    for letter in text + ".":  
        if letter in params_game.nickname_symbols and start:  # если буква есть, в допустимых символах ника
            username += letter

        else:
            start = False
            if username:
                all_usernames.append("@" + username)
                username = ""

            if letter == "@":  # начать запись
                start = True

    return all_usernames


def create_dialog(text: str, value) -> str:
    """создание диалога, вместо "?", будут по очереди вставляться значения из value.

    Args:
        text (str): сообщение, над которым работаем.
        value (_type_): значения, которые будут подставлены вместо "?".

    Returns:
        str: возвращает измененную строку.
    """
    index_value = 0  # индекс элемента в value
    dialog_message = ""  # навое значение в value 

    for i, elem in enumerate(text):
        if elem == "?":
            dialog_message += value[index_value]
            index_value += 1  # увеличить индекс, value  

            # если все значения value, вставлены, то перестать перебирать значения 
            if index_value == len(value) - 1:  
                dialog_message += text[i + 1 : -1]
                break
        else:
            dialog_message += elem

    return dialog_message
