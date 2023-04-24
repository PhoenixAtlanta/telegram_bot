import os 
import json


IMAGES_DIR = "images"
JSON_PATH = "data_file/picture_data.json"


def find_last_files(directory: str, all_image: list=[]) -> list:

    for filename in os.listdir(directory):
        one_file = os.path.join(directory, filename)

        if os.path.isfile(one_file):
            all_image.append(one_file)

        else:
            find_last_files(one_file, all_image)
    
    return all_image


def get_data_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

        return data
    

def write_data_json(path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


def update_data(path: str, key: str, data: dict) -> None:
    old_data = get_data_json(path)
    old_data[key] = data

    write_data_json(path, old_data)

