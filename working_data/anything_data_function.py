import os 


IMAGES_DIR = "images"
JSON_PATH = "data_file/picture_data.json"


def find_last_files(directory: str, all_image: list=[]) -> list:

    for filename in os.listdir(directory):
        one_file = os.path.join(directory, filename)

        if os.path.isfile(one_file):
            all_image.append(one_file.split("\\")[-1])

        else:
            find_last_files(one_file, all_image)
    
    return all_image
