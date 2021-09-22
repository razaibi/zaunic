import os
from pathlib import Path
from zcore.common import FileManager
import CONFIGS
from zcore.processor.node_service import NodeProcessorService
from zcore.secret.manager import Factory as SecretsFactory
from zcore.processor.service import ProcessorService
from zcore.action.generator_service import GeneratorActionService
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

    
    def get_playbook_data(self,playbook_name)->dict:
        fm = FileManager()
        playbook_data = fm.read_yaml(
            os.path.join(
                CONFIGS.PLAYBOOKS_FOLDER,
                '{}.yml'.format(playbook_name)
            )
        )


    def impute_secrets(self, playbook_data)->dict:
        secrets_service = SecretsFactory("zaunic")
        playbook_data = secrets_service.impute_secrets(playbook_data)
        return playbook_data

    def process_playbook(self, playbook_name):
        #playbook
        fm = FileManager()
        playbook_data = fm.read_yaml(
            os.path.join(
                CONFIGS.PLAYBOOKS_FOLDER,
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
    def perform_action(node, node_processor_service, playbook_name, playbook_data):
        if node['hostname'] in CONFIGS.LOCAL_NODE_TAGS:
            #Do something on local node
            bar = ChargingBar(
                'Processing {} on {}'.format(playbook_name, node["name"]), 
                max=len(playbook_data['tasks'])
            )
            [PlaybookProcessorService.generate_content_local(task, playbook_data['secrets']) for task in playbook_data['tasks']]
            bar.finish()
        else:

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
                [PlaybookProcessorService.generate_content(task, playbook_data['secrets'], node_client, ftp_client) for task in playbook_data['tasks']]

                #    bar.next()
                ftp_client.close()
                node_client.close()
                bar.finish()
            return node_connection

    @staticmethod
    def generate_content(task, secrets, node_client, ftp_client):
        if 'secrets' not in task:
            task['secrets'] = {}
        task['secrets'] = secrets
        task_template = GeneratorActionService.generate_task_code(**task)
        task_output_path = PlaybookProcessorService.get_output_path(task)
        #node
        NodeProcessorService.write_to_remote_file(
            node_client,
            ftp_client,
            task_output_path,
            task_template
        )

    @staticmethod
    def generate_content_local(task, secrets):
        if 'secrets' not in task:
            task['secrets'] = {}
        task['secrets'] = secrets
        task_template = GeneratorActionService.generate_task_code(**task)
        task_output_path = PlaybookProcessorService.get_output_path(task)
        #node
        NodeProcessorService.write_to_local_file(
            task_output_path,
            task_template
        )




