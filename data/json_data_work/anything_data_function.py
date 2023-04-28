import os
import json


PATH_DIALOG_JSON = "data/data_file/dialog_data.json"  # путь json файла с диалогом


def find_last_files(directory: str, all_image: list = []) -> list:
    """рекурсивно перебирает все папки, пока не дойдет до какого-то файла

    Args:
        directory (str): Название директории.
        all_image (list, optional): Список файлов. Defaults to [].

    Returns:
        list: возвращает все файлы в директории
    """
    for filename in os.listdir(directory):
        one_file = os.path.join(directory, filename)

        if os.path.isfile(one_file):
            all_image.append(one_file.split("\\")[-1])

        else:
            find_last_files(one_file, all_image)

    return all_image


def get_all_dialog() -> dict:
    with open(PATH_DIALOG_JSON, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

        return data


def dialog(name_dialog: str) -> str:
    data = get_all_dialog()
    result = data[name_dialog]

    return result
