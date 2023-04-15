from dataclasses import dataclass, field
from typing import List


all_cards = ["профессия", "здоровье", "биологические характеристики",
              "хобби", "фобии", "дополнительная информация",
                "человеческие качества", "Специальные условия 1",
                  "Специальные условия 2"]

buttons_name = {
    "player_buttons": ("/кто", "/leave"),
    "card": all_cards.copy(),
    "step": ("/all", "Кто ходит"),

}


@dataclass
class ParamsGame:
    ID: str = ""
    players: List = field(default_factory=lambda: [])
    step: int = 1
    player: int = 0


def set_params() -> dict:
    """return dict with all value dataclass value"""

    params_bot = {
        "params_game": ParamsGame(),
    }

    return params_bot
    
