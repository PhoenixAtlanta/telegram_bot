import os.path
import json
from random import choice

import working_data.anything_data_function as data_function



class DataJson:
    IMAGES_DIR = "images"
    DATA_JSON_DIR = "data_file"
    NAME_DATABASE_JSON = "picture_data.json"

    parameter_template = {
        "type_image": "",
        "name": "",
        "path_to_image": "",
        "description": "" 
    }

    @property
    def image_dir(self) -> str:
        return self.IMAGES_DIR
    
    @image_dir.setter
    def image_dir(self, directory: str) -> None:
        self.IMAGES_DIR = directory

    @property
    def data_json_dir(self) -> str:
        return self.data_json_dir
    

    @data_json_dir.setter
    def data_json_dir(self, directory: str) -> None:
        self.DATA_JSON_DIR = directory


    @property
    def name_database_json(self) -> str:
        return self.NAME_DATABASE_JSON
    

    @name_database_json.setter
    def directory(self, directory: str) -> None:
        self.NAME_DATABASE_JSON = directory


    @classmethod
    def get_data_path(cls) -> str:
        return f"{cls.DATA_JSON_DIR}\\{cls.NAME_DATABASE_JSON}"


    def __init__(self):
        self.path_database = self.get_data_path()

    
    def create_data(self) -> None:
        if not os.path.exists(self.path_database):
            all_path_image = data_function.find_last_files(self.IMAGES_DIR)

            for image_path in all_path_image:
                type_image = image_path.split("\\")[1]
                name = image_path.split("\\")[-1][:-4].lower()

                data_image = self.fill_data_image(type_image=type_image, name=name, path_to_image=image_path, description=f"{type_image};{name}")

                data_function.update_data(path=self.path_database, key=name, data=data_image)

        

    def fill_data_image(self, type_image: str, name: str, path_to_image: str, description: str=""):
        data_image = self.parameter_template.copy()

        data_image["type_image"] = type_image
        data_image["name"] = name
        data_image["path_to_image"] = path_to_image
        data_image["description"] = description

        return data_image


    def get_data_json(self) -> dict:
        with open(self.path_database, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

            return data
        

    def write_data_json(path, data: dict) -> None:
        with open(path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)


    def update_data(self, key: str, data: dict) -> None:
        old_data = self.get_data_json(self.path_database)
        old_data[key] = data

        self.write_data_json(self.path_database, old_data)


    def get_inf_cart(self, name: str, key: str=None) -> dict:
        data = self.get_data_json(self.path_database)
        inf_cart = data[name]

        if key is None:
            return inf_cart
        return inf_cart[key]
    

    def get_data_image(self, type_image: str) -> str:
        data = self.get_data_json()
        name = choice(data[type_image])[:-4].lower()
        data_image = data["all_photo_data"][name]

        return data_image


