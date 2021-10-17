from abc import ABC, abstractmethod
from zcore.action.service import ActionService
import os
from zcore import logger
from typing import List, Tuple
from zcore.common import FileManager
from zcore.template.manager import Factory as TemplateFactory
import CONFIGS
import requests

class RestApiActionService(ActionService):
    def __init__(self):
        self.log = logger.LogMachine()

    @staticmethod
    def call_endpoint(params_dict):
        if 'headers' not in params_dict['task']['request']:
            params_dict['task']['request']['headers'] = None

        if 'body' not in params_dict['task']['request']:
            params_dict['task']['request']['body'] = None
        
        if 'params' not in params_dict['task']['request']:
            params_dict['task']['request']['params'] = None

        switcher = {
            "get": RestApiActionService.make_get_request,
            "post": RestApiActionService.make_post_request,
            "put": RestApiActionService.make_put_request,
            "patch": RestApiActionService.make_get_request,
            "delete": RestApiActionService.make_get_request 
        }
        
        response = switcher[params_dict['task']['request']['method'].lower()](
            params_dict['task']['request']
        )

        response_content = RestApiActionService.parse_response(
            params_dict['task']['request']['return'],
            response
        )

        #print('\n')
        #print(response_content)

    @staticmethod
    def make_get_request(request_details):
        response = requests.get(
            request_details['url'], 
            params=request_details['params']
        )
        return response

    @staticmethod
    def make_post_request(request_details):
        response = requests.post(
            request_details['url'], 
            params=request_details['params'],
            data=request_details['body']
        )
        return response

    @staticmethod
    def make_put_request(request_details):
        response = requests.put(
            request_details['url'], 
            params=request_details['params'],
            data=request_details['body']
        )
        return response


    @staticmethod
    def parse_response(return_details: str, response=None):
        response_content=None
        if (response.status_code == return_details['status_code']):
            if 'type' in return_details:
                if return_details['type']=='json':
                    response_content = response.json()
                if return_details['type']=='text':
                    response_content = response.text
            response_content
        return response_content
    
        