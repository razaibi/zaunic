from abc import ABC, abstractmethod
from zcore.action.service import ActionService
import os
from zcore import logger
from typing import Dict, List, Tuple
from zcore.common import FileManager
from zcore.template.manager import Factory as TemplateFactory
import CONFIGS
import requests
import json
from urllib.parse import urlencode

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

        if 'mode' not in params_dict['task']:
            params_dict['task']['mode'] = 'remote'

        switcher = {
            "get_remote": RestApiActionService.make_remote_get_request,
            "get_local": RestApiActionService.make_local_get_request,
            "post_remote": RestApiActionService.make_remote_post_request,
            "post_local": RestApiActionService.make_local_post_request,
            "put_remote": RestApiActionService.make_remote_put_request,
            "put_local": RestApiActionService.make_local_put_request
        }

        # Prepare method name based on declaration and call type.
        switcher_method = params_dict['task']['request']['method'].lower() + '_' + params_dict['task']['mode']

        response = switcher[switcher_method](
            params_dict['node_client'],
            params_dict['task']['request']
        )

        # Switch between remote and local invocations.
        if params_dict['task']['mode'] == 'remote':
            response_content = RestApiActionService.parse_remote_response(
                params_dict['task']['request']['return'],
                response
            )
        else:
            response_content = RestApiActionService.parse_local_response(
                params_dict['task']['request']['return'],
                response
            )

        #print(response_content)

    @staticmethod
    def make_remote_get_request(node_client, request_details):
        if request_details['params'] is not None:
            query_params = urlencode(request_details['params'])
        else:
            query_params = None
        command='curl "{0}?{1}"'.format(
            request_details['url'],
            query_params
        )
        stdin, stdout, ssh_stderr = node_client.exec_command('{0}'.format(command))
        ret = stdout.read()
        return ret.decode('ascii')
        
    @staticmethod
    def make_local_get_request(node_client, request_details):
        response = requests.get(
            request_details['url'], 
            params=request_details['params']
        )
        return response

    @staticmethod
    def make_remote_post_request(node_client, request_details):
        if request_details['params'] is not None:
            query_params = urlencode(request_details['params'])
        else:
            query_params = None
        command='curl -v -X POST "{0}?{1}" -H "Content-Type: application/{2}" -d "{3}"  >> {4}'.format(
            request_details['url'],
            query_params,
            request_details['return']['type'],
            str(request_details['body']),
            request_details['output']
        )
        
        stdin, stdout, ssh_stderr = node_client.exec_command('{0}'.format(command))
        ret = stdout.read()
        return ret.decode('ascii')

    @staticmethod
    def make_local_post_request(node_client, request_details):
        response = requests.post(
            request_details['url'], 
            params=request_details['params'],
            data=request_details['body']
        )
        return response

    @staticmethod
    def make_remote_put_request(node_client, request_details):
        if request_details['params'] is not None:
            query_params = urlencode(request_details['params'])
        else:
            query_params = None
        command='curl -X PUT "{0}?{1}" -H "Content-Type: application/{2}" -d "{3}" >> {4}'.format(
            request_details['url'],
            query_params,
            request_details['return']['type'],
            str(request_details['body']),
            request_details['ouput']
        )
        
        stdin, stdout, ssh_stderr = node_client.exec_command('{0}'.format(command))
        ret = stdout.read()
        return ret.decode('ascii')

    @staticmethod
    def make_local_put_request(node_client, request_details):
        response = requests.put(
            request_details['url'], 
            params=request_details['params'],
            data=request_details['body']
        )
        return response

    @staticmethod
    def parse_remote_response(return_details: Dict, response=None):
        response_content=None
        if 'type' in return_details:
            if return_details['type']=='json':
                try:
                    response_content = json.loads(response)
                except:
                    response_content=''
            if return_details['type']=='text':
                response_content = response
        return response_content

    @staticmethod
    def parse_local_response(return_details: Dict, response=None):
        response_content=None
        if (response.status_code == return_details['status_code']):
            if 'type' in return_details:
                if return_details['type']=='json':
                    try:
                        response_content = json.loads(response)
                    except:
                        response_content=''
                if return_details['type']=='text':
                    response_content = response.text
            response_content
        return response_content
    
        