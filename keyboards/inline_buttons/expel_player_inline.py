from ..inline_buttons.create_inline_buttons import create_inline

expel_player_value = {"исключить игрока": {"number": 0, "callback": "исключить игрока"}, "оставить игрока": {"number": 0, "callback": "оставить игрока"}}
    
expel_player_keyboard = create_inline(expel_player_value, type_placement="add")