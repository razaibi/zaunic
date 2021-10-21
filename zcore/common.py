from typing import Dict
import yaml
import os
import requests

class FileManager():
    def __init__(self):
        pass

    def read_yaml(self, file_path:str)->str:
        documents=None
        with open(file_path) as file:
            documents = yaml.load(file, Loader=yaml.FullLoader)
        return documents

    def read_file(self, file_path:str)->str:
        with open(file_path) as f:
            contents = f.read()
        return contents

    def write_yaml(self, file_path:str, content:Dict)->str:
        with open(file_path, 'w') as file:
            documents = yaml.dump(content, file)


class ApiClientManager():
    def __init__(self):
        pass

    def get(self, url, headers=None):
        response = requests.get(url=url, headers=headers)
        return response

    def post(self, url, data=None, json=None, headers=None):
        response = requests.post(
            url=url,
            data=data,
            json=json, 
            headers=headers
        )
        return response

    def authenticate(self, url):
        pass


