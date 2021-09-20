from typing import Tuple
from paramiko.client import SSHClient
import os
from zcore.common import FileManager
import paramiko

class Manager():
    def __init__(self):
        self.fm = FileManager()

    def read_node_list(self, node_file_name:str)->list:
        node_list_obj = self.fm.read_yaml(
            os.path.join(
                'nodes',
                '{0}.yml'.format(
                    node_file_name
                )
            )
        )
        return node_list_obj['nodes']

    def connect_node_with_creds(self, hostname:str, host_username:str, host_password:str)->dict:
        try:
            ssh_client=paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(
                hostname=hostname,
                username=host_username,
                password=host_password
            )
            return {
                "state" : "ok",
                "client" : ssh_client
            }
        except Exception as e:  
            return { 
                "state" : "error",
                "message" : str(e)
            }

    def exec_command(
        self,
        node_client: SSHClient,
        command:str
        )->Tuple:
        stdin,stdout,stderr = node_client.exec_command(command)
        return (stdin, stdout, stderr)



