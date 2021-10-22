import paramiko
from paramiko.client import SSHClient
from scp import SCPClient
from typing import Tuple
import os
import errno
from posixpath import expanduser
from zcore.common import FileManager
from zcore.processor.service import ProcessorService

class NodeProcessorService(ProcessorService):
    def __init__(self) -> None:
        pass

    def read_list(self, node_file_name:str)->list:
        fm = FileManager()
        node_list_obj = fm.read_yaml(
            os.path.join(
                'nodes',
                '{0}.yml'.format(
                    node_file_name
                )
            )
        )
        return node_list_obj['nodes']

    def get_nodes(self, taskflow_data):
        node_list = None
        if 'nodes' in taskflow_data:
            node_list = self.read_list(
                taskflow_data['nodes']
            )

        return node_list

    def connect_node_with_creds(self, hostname:str, host_username:str, host_password:str)->dict:
        try:
            ssh_client=paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(
                hostname=hostname,
                username=host_username,
                password=host_password
            )
            scp_client = SCPClient(ssh_client.get_transport())
            return {
                "state" : "ok",
                "client" : ssh_client,
                "scp_client" : scp_client
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

    @staticmethod
    def write_to_remote_file(
            node_client,
            ftp_client,
            file_path, 
            content
        ):
        folder_path = os.path.dirname(file_path)
        # Create temp folder.
        temp_folder = str(os.path.join(os.sep, "tmp","zaunic"))
        node_client.exec_command("sudo mkdir -p {0}".format(temp_folder))
        clean_file_path = file_path.replace(folder_path,'').replace(os.sep,'')
        #Upload to tmp folder
        file = ftp_client.file(os.path.join(temp_folder,clean_file_path), "w", -1)
        file.write(content)
        file.flush()
        # Move to designated folder
        node_client.exec_command("sudo mkdir -p {0}".format(folder_path))
        node_client.exec_command(
                "sudo mv {0}{1}* {2}{3}".format(
                temp_folder, 
                os.sep,
                folder_path, 
                os.sep
            )
        )

    @staticmethod
    def execute_remote_file(
            node_client,
            command
        ):
        node_client.exec_command("{0}".format(command))

    @staticmethod
    def write_to_local_file(file_path, content):
        folder_path = os.path.dirname(file_path)
        if not os.path.exists(os.path.expanduser(folder_path)):
            try:
                os.makedirs(os.path.expanduser(folder_path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        expanded_path=None
        if folder_path.startswith("~"):
            expanded_path = os.path.expanduser(file_path)
        else:
            expanded_path = os.path.join(
                os.getcwd(),
                file_path
            )
        with open(expanded_path, "w+") as f:
            f.write(content)