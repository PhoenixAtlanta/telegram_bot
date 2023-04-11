from dataclasses import dataclass, field
from typing import List


@dataclass
class ParamsGame:
    ID: str = ""
    players: List = field(default_factory=lambda: [])


def set_params() -> dict:
    """return dict with all value dataclass value"""

    params_bot = {
        "params_game": ParamsGame()
    }

    return params_bot
    
