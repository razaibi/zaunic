import os
from pathlib import Path
from zcore.common import FileManager
import CONFIGS
from zcore.processor.node_service import NodeProcessorService
from zcore.secret.orchestrator_service import OrchestratorService
from zcore.processor.service import ProcessorService
from zcore.action.generator_service import GeneratorActionService
from zcore.action.executor_service import ExecutorActionService
from progress.bar import ChargingBar

class PlaybookProcessorService(ProcessorService):
    def __init__(self) -> None:
        pass

    def read_list(self) -> list:
        fm = FileManager()
        playbook_list = fm.read_yaml(
            os.path.join(
                CONFIGS.RUNNER_FOLDER,
                '{}.yml'.format('running_list')
            )
        )
        return playbook_list

    def read_element(
            self,
            element
        ):
        pass


    def get_playbook_data(self,playbook_name)->dict:
        fm = FileManager()
        playbook_data = fm.read_yaml(
            os.path.join(
                CONFIGS.TASK,
                '{}.yml'.format(playbook_name)
            )
        )

    def impute_secrets(self, playbook_data)->dict:
        if CONFIGS.SECRETS_KEY in playbook_data:
            secrets_service = OrchestratorService()
            playbook_data = secrets_service.impute_secrets(playbook_data)
        return playbook_data

    def process_playbook(self, playbook_name):
        #playbook
        fm = FileManager()
        playbook_data = fm.read_yaml(
            os.path.join(
                CONFIGS.TASKFLOWS_FOLDER,
                '{}.yml'.format(playbook_name)
            )
        )

        node_processor_service = NodeProcessorService()
        node_list = node_processor_service.get_nodes(playbook_data)

        #playbook
        playbook_data = self.impute_secrets(playbook_data)
        result = [PlaybookProcessorService.perform_action(node, node_processor_service, playbook_name, playbook_data) for node in node_list]

        #for node in node_list:
        #    #node

    @staticmethod
    def action_switcher(params_dict) -> None:
        action = {
           'generate' : PlaybookProcessorService.call_generate_action, 
           'copy' : PlaybookProcessorService.call_generate_action, 
           'call_api' : PlaybookProcessorService.call_generate_action, 
           'execute' : PlaybookProcessorService.call_execute_action
        }
        action[params_dict['task']['action']](**params_dict)

    @staticmethod
    def perform_action(node, node_processor_service, playbook_name, playbook_data):
        #Plug Secrets into 
        playbook_data = PlaybookProcessorService.validate_playbook_struct(playbook_data)
        node_connection = node_processor_service.connect_node_with_creds(
            node['hostname'],
            node['username'],
            node['password']
        )
        if node_connection['state']=="ok":
            node_client = node_connection["client"]
            ftp_client = node_client.open_sftp()
            bar = ChargingBar(
                'Processing {} on {}'.format(playbook_name, node["name"]), 
                max=len(playbook_data['tasks'])
            )
            ## For Generation tasks, invoke generator service.

            for task in playbook_data['tasks']:
                PlaybookProcessorService.action_switcher(
                    {
                        "task": task,
                        "playbook_data": playbook_data,
                        "node_client": node_client,
                        "ftp_client": ftp_client,
                        "node_processor_service": NodeProcessorService 
                    }
                )

            #    bar.next()
            ftp_client.close()
            node_client.close()
            bar.finish()
        return node_connection


        #if node['hostname'] in CONFIGS.LOCAL_NODE_TAGS:
        #    bar = ChargingBar(
        #        'Processing {} on {}'.format(playbook_name, node["name"]), 
        #        max=len(playbook_data['tasks'])
        #    )
        #    [PlaybookProcessorService.generate_content_local(task, playbook_data['secrets']) for task in playbook_data['tasks']]
        #    bar.finish()
        #else:
        #    node_connection = node_processor_service.connect_node_with_creds(
        #        node['hostname'],
        #        node['username'],
        #        node['password']
        #    )
        #    if node_connection['state']=="ok":
        #        node_client = node_connection["client"]
        #        ftp_client = node_client.open_sftp()
        #        bar = ChargingBar(
        #            'Processing {} on {}'.format(playbook_name, node["name"]), 
        #            max=len(playbook_data['tasks'])
        #        )
        #        ## For Generation tasks, invoke generator service.
        #        [PlaybookProcessorService.generate_content_remote(task, playbook_data['secrets'], node_client, ftp_client) for task in playbook_data['tasks']]
#
        #        #    bar.next()
        #        ftp_client.close()
        #        node_client.close()
        #        bar.finish()
        #    return node_connection

    @staticmethod
    def validate_playbook_struct(playbook_data):
        if CONFIGS.SECRETS_KEY not in playbook_data:
            playbook_data['secrets'] = None
        return playbook_data

    @staticmethod
    def call_generate_action(task, playbook_data, node_client, ftp_client, node_processor_service):
        GeneratorActionService.generate_content_remote(
            task, 
            playbook_data['secrets'], 
            node_client, 
            ftp_client,
            node_processor_service
        )

    @staticmethod
    def call_execute_action(task, playbook_data, node_client, ftp_client, node_processor_service):
        ExecutorActionService.execute_command(
            task,
            node_client
        )








