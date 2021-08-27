import yaml
import os

class FileManager():
    def __init__(self):
        pass

    def read_yaml(self, file_path:str)->str:
        documents=None
        with open(file_path) as file:
            documents = yaml.load(file, Loader=yaml.FullLoader)
        return documents

