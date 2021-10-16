from abc import ABC, abstractmethod
from zcore.action.service import ActionService
import os
from zcore import logger
from typing import List, Tuple
from zcore.common import FileManager
from zcore.template.manager import Factory as TemplateFactory
import CONFIGS

class FileActionService(ActionService):
    def __init__(self):
        self.log = logger.LogMachine()

    @staticmethod
    def upload_file(params_dict):
        try:
            params_dict['ftp_client'].put(
                params_dict['task']['source'],
                params_dict['task']['destination']
            )
        except FileNotFoundError:
            print(
                'Check if source file mentioned in the taskflow exists.'
            )
        except Exception as e:  
            print(e)

    @staticmethod
    def download_file(params_dict):
        params_dict['ftp_client'].get(
            params_dict['task']['source'],
            params_dict['task']['destination']
        )