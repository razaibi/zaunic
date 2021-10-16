from abc import ABC, abstractmethod
from zcore.action.service import ActionService
import os
from zcore import logger
from typing import List, Tuple
from zcore.common import FileManager
from zcore.template.manager import Factory as TemplateFactory
import CONFIGS

class GeneratorActionService(ActionService):
    def __init__(self):
        self.log = logger.LogMachine()

    @staticmethod
    def generate_content_remote(params_dict):
        if 'secrets' not in params_dict['task']:
            params_dict['task']['secrets'] = {}
        params_dict['task']['secrets'] = params_dict['taskflow_data']['secrets']
        task_template = GeneratorActionService.generate_task_code(**params_dict['task'])
        task_output_path = GeneratorActionService.get_output_path(params_dict['task'])

        params_dict['node_processor_service'].write_to_remote_file(
            params_dict['node_client'],
            params_dict['ftp_client'],
            task_output_path,
            task_template
        )

        ##params_dict['task']

        #if 'secrets' not in params_dict['task']:
        #    task['secrets'] = {}
        #task['secrets'] = secrets
        #task_template = GeneratorActionService.generate_task_code(**task)
        #task_output_path = GeneratorActionService.get_output_path(task)
        #
        #NodeProcessorInstance.write_to_remote_file(
        #    node_client,
        #    ftp_client,
        #    task_output_path,
        #    task_template
        #)

    @staticmethod
    def generate_content_local(task, secrets, NodeProcessorInstance):
        if 'secrets' not in task:
            task['secrets'] = {}
        task['secrets'] = secrets
        task_template = GeneratorActionService.generate_task_code(**task)
        task_output_path = GeneratorActionService.get_output_path(task)
        #node
        NodeProcessorInstance.write_to_local_file(
            task_output_path,
            task_template
        )

    @staticmethod
    def get_output_path(task):
        ##Prepare output path
        output_file_path = os.path.join(
            '{}'.format(task[
                CONFIGS.OUTPUT_KEY   
            ].replace(
                CONFIGS.OUTPUT_FOLDER_SEPARATOR,
                os.sep
                )
            )
        )
        return output_file_path

    @staticmethod
    def generate_task_code(
            **task
        ):
        """
        Get raw data from "source_data" folder to inject in the template.
        """
        data_injector = GeneratorActionService.get_data_injector(task)

        data_injector = GeneratorActionService.apply_data_sub_expression(
            task, data_injector
        )

        template_service = TemplateFactory("jinja")

        _rendered_template = template_service.render_template(
            task, data_injector
        )

        return _rendered_template

    @staticmethod
    def get_data_injector(task):
        if CONFIGS.DATA_KEY in task:
            fm = FileManager()
            data_injector = fm.read_yaml(
                os.path.join(
                    CONFIGS.SOURCE_DATA_FOLDER,
                    "{}.yml".format(
                        task['data'].replace(
                            CONFIGS.DATA_FOLDER_SEPARATOR,
                            os.sep
                        )
                    )
                )
            )
            return data_injector
        else:
            return None

    @staticmethod
    def apply_data_sub_expression(task, data_injector):
        """
        Extract data from data levels
        """
        if CONFIGS.DATA_LEVEL_KEY in task:
            task_data_level = task[CONFIGS.DATA_LEVEL_KEY]
            task_data_level = \
                task_data_level.replace(" ","")
            sub_expression = GeneratorActionService.process_data_level(
                task_data_level
            )

            """ 
            Apply sub expression to data.
            """
            data_injector[CONFIGS.DATA_KEY] = \
                eval(
                    "".join(
                        [
                            "data_injector['{}']".format(
                                CONFIGS.DATA_KEY
                            ),
                            sub_expression
                        ]
                    )
                )
        return data_injector

    @staticmethod
    def process_data_level(level_expression):
        levels = level_expression.split(
            CONFIGS.DATA_LEVEL_SEPARATOR
        )
        level_list = list(map(GeneratorActionService.fix_type, levels))
        refined_expression = "".join(level_list)
        return refined_expression

    @staticmethod
    def fix_type(item):
        """
        Assign type as int or string to item.
        Quick hack.
        TODO: Refactor
        """
        try:
            int(item)
            return "[" + str(item) + "]"
        except:
            return "['" + str(item) + "']"