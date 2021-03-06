from abc import ABC, abstractmethod
from zcore.action.service import ActionService
import os
from zcore import logger
from typing import List, Tuple
from zcore.common import FileManager
from zcore.template.manager import Factory as TemplateFactory
import CONFIGS

class ExecutorActionService(ActionService):
    def __init__(self):
        self.log = logger.LogMachine()

    @staticmethod
    def execute_command(params_dict):
        params_dict['node_client'].exec_command(
            "{0}".format(params_dict['task']['command'])
        )