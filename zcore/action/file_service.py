from abc import ABC, abstractmethod
from zcore.action.service import ActionService
import os
from zcore import logger
from typing import List, Tuple
from zcore.common import FileManager
from pathlib import Path
from zcore.template.manager import Factory as TemplateFactory
import CONFIGS
import fnmatch
import glob

class FileActionService(ActionService):
    def __init__(self):
        self.log = logger.LogMachine()

    @staticmethod
    def upload_file(params_dict):
        try:
            files_to_upload = FileActionService.process_source_files(params_dict['task']['source'])

            if params_dict['task']['source'].endswith(CONFIGS.SOURCE_WILDCARD):
                params_dict['scp_client'].put(
                    glob.glob(params_dict['task']['source']),
                    params_dict['task']['destination']
                )
            else:
                params_dict['ftp_client'].put(
                    files_to_upload,
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

    @staticmethod
    def process_source_files(source_files_path):
        if source_files_path.endswith(CONFIGS.SOURCE_WILDCARD):
            return glob.glob(source_files_path)
        else:
            return source_files_path

