import json

PATH_DIALOG_JSON = "data_file/dialog_data.json"

def get_all_dialog() -> dict:
    with open(PATH_DIALOG_JSON, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

        return data


def dialog(name_dialog: str) -> str:
    data = get_all_dialog()
    result = data[name_dialog]

    return result 
