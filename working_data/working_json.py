import json
import pprint


async def read_json(name: str="data_file/game_json.json"):
    """возвращает данные, которые хранятся в json"""
    with open(name, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


async def write_data(data, name: str="data_file/game_json.json"):
    """записывает данные в json файл"""
    with open(name, "w") as json_file:
        pprint.pprint(data)

        json.dump(data, json_file, indent=4)

