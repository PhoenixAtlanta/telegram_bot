import json

from app import bot_params


async def read_data(name_file: str=bot_params["name_json"]):
    """получить данные"""
    async with open(name_file, "r") as json_file:
        return json.load(json_file)
    

async def write_data(data: dict, name_file: str=bot_params["name_json"]):
    """записать данные"""
    async with open(name_file, "w") as json_file:
        json.dump(data, json_file)
        


async def writing_admin(admin_ad: int):
    """запись id администратора(создателя игры)"""

    data = await read_data()
    
    data = data["admin_id"] = admin_ad

    write_data(data=data)

    




