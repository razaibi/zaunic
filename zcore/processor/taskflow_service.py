import os
from pathlib import Path
from zcore.common import FileManager
import CONFIGS
from zcore.node import Manager as NodeManager
from zcore.processor.node_service import NodeProcessorService
from zcore.secret.orchestrator_service import OrchestratorService
from zcore.processor.service import ProcessorService
from zcore.action.generator_service import GeneratorActionService
from zcore.action.executor_service import ExecutorActionService
from zcore.action.file_service import FileActionService
from zcore.action.rest_api_service import RestApiActionService
from progress.bar import ChargingBar

class TaskflowProcessorService(ProcessorService):
    def __init__(self) -> None:
        pass

    def read_list(self) -> list:
        fm = FileManager()
        taskflow_list = fm.read_yaml(
            os.path.join(
                CONFIGS.RUNNER_FOLDER,
                '{}.yml'.format('running_list')
            )
        )
        return taskflow_list

    def read_element(
            self,
            element
        ):
        pass


    def get_taskflow_data(self,taskflow_name)->dict:
        fm = FileManager()
        taskflow_data = fm.read_yaml(
            os.path.join(
                CONFIGS.TASK,
                '{}.yml'.format(taskflow_name)
            )
        )

    def impute_secrets(self, taskflow_data)->dict:
        if CONFIGS.SECRETS_KEY in taskflow_data:
            secrets_service = OrchestratorService()
            taskflow_data = secrets_service.impute_secrets(taskflow_data)
        return taskflow_data

    def process_taskflow(self, taskflow_name):
        #taskflow
        fm = FileManager()
        taskflow_data = fm.read_yaml(
            os.path.join(
                CONFIGS.TASKFLOWS_FOLDER,
                '{}.yml'.format(taskflow_name)
            )
        )

        node_processor_service = NodeProcessorService()
        node_list = node_processor_service.get_nodes(taskflow_data)
        nm = NodeManager()
        node_list = nm.get_creds_nodes(node_list)
        
        #taskflow
        taskflow_data = self.impute_secrets(taskflow_data)
        result = [TaskflowProcessorService.perform_action(node, node_processor_service, taskflow_name, taskflow_data) for node in node_list]

    @staticmethod
    def action_switcher(params_dict) -> None:
        action = {
           'generate' : GeneratorActionService.generate_content_remote, 
           'upload' : FileActionService.upload_file, 
           'download' : FileActionService.download_file, 
           'call_rest_api' : RestApiActionService.call_endpoint, 
           'execute' : ExecutorActionService.execute_command
        }
        try:
            action[params_dict['task']['action']](params_dict)
        except KeyError as e:
            print(e)
            print('\nUndefined action. Check your task "action" value.')

    @staticmethod
    def perform_action(node, node_processor_service, taskflow_name, taskflow_data):
        #Plug Secrets into 
        taskflow_data = TaskflowProcessorService.validate_taskflow_struct(taskflow_data)
        node_connection = node_processor_service.connect_node_with_creds(
            node['hostname'],
            node['username'],
            node['password']
        )
        if node_connection['state']=="ok":
            node_client = node_connection["client"]
            scp_client = node_connection["scp_client"]
            ftp_client = node_client.open_sftp()
            bar = ChargingBar(
                'Processing {} on {}'.format(taskflow_name, node["name"]), 
                max=len(taskflow_data['tasks'])
            )
            ## For Generation tasks, invoke generator service.

            for task in taskflow_data['tasks']:
                bar.next()
                TaskflowProcessorService.action_switcher(
                    {
                        "task": task,
                        "taskflow_data": taskflow_data,
                        "node_client": node_client,
                        "scp_client" : scp_client,
                        "ftp_client": ftp_client,
                        "node_processor_service": NodeProcessorService,

                    }
                )
                
            ftp_client.close()
            scp_client.close()
            node_client.close()
            bar.finish()
        else:
            print(f'Unable to connect to node(s) for "{taskflow_name}" taskflow.')
        return node_connection

    @staticmethod
    def validate_taskflow_struct(taskflow_data):
        if CONFIGS.SECRETS_KEY not in taskflow_data:
            taskflow_data['secrets'] = None
        return taskflow_data








