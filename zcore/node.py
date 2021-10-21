from typing import List, Tuple
from paramiko.client import SSHClient
import os
from zcore import common
from zcore.common import FileManager
import paramiko
from cryptography.fernet import Fernet
from slugify import slugify
from pathlib import Path
import CONFIGS

class Manager():
    def __init__(self):
        self.fm = FileManager()

    def read_node_list(self, node_file_name:str)->list:
        node_list_obj = {}
        try:
            node_list_obj = self.fm.read_yaml(
                os.path.join(
                    'nodes',
                    '{0}.yml'.format(
                        node_file_name
                    )
                )
            )
        except Exception as e:
            node_list_obj['nodes'] = []
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

    def add_node_with_credentials(
            self,
            group_name: str,
            name: str,
            host: str,
            username: str,
            password: str
        ):
        node_encryption_key = self._get_encryption_key()
        f = Fernet(bytes(node_encryption_key, "utf-8"))
        encrypted_username = f.encrypt(username)
        encrypted_password = f.encrypt(password)
        slugified_group_name = slugify(group_name)
        new_node_dict = {
            "name": "{}".format(name),
            "protocol": "ssh",
            "hostname": host,
            "connection_mode": "credentials",
            "username": encrypted_username.decode("utf-8"),
            "password": encrypted_password.decode("utf-8")
        }
        node_list = self.read_node_list(slugified_group_name)
        if node_list is None:
            node_list = []
        matching_node_index_by_name = self._find_by_index(node_list, 'name', name)
        matching_node_index_by_hostname = self._find_by_index(node_list, 'hostname', host)
        
        if matching_node_index_by_name > -1 or matching_node_index_by_hostname > -1:
            print(f'Node with matching Name/Hostname already exists.')
        else:
            #Node does not exist.
            node_list.append(new_node_dict)
            self.fm.write_yaml(
                os.path.join(
                    'nodes',
                    '{}.yml'.format(slugified_group_name)
                ),
                { 'nodes' : node_list}
            )
            print('Added node to {} group.'.format(slugified_group_name))


    def update_node_by_name(
            self,
            group_name: str,
            name: str,
            host: str,        
            username: str,
            password: str
        ):
        slugified_group_name = slugify(group_name)
        node_encryption_key = self._get_encryption_key()
        f = Fernet(bytes(node_encryption_key, "utf-8"))
        encrypted_username = f.encrypt(username)
        encrypted_password = f.encrypt(password)
        node_list = self.read_node_list(slugified_group_name)
        matching_node_index_by_name = self._find_by_index(node_list, 'name', name)
        if matching_node_index_by_name > -1:
            new_node_dict = {
                "name": "{}".format(name),
                "protocol": "ssh",
                "hostname": host,
                "connection_mode": "credentials",
                "username": encrypted_username.decode("utf-8"),
                "password": encrypted_password.decode("utf-8")
            }
            node_list[matching_node_index_by_name] = new_node_dict
            self.fm.write_yaml(
                os.path.join(
                    'nodes',
                    '{}.yml'.format(slugified_group_name)
                ),
                { 'nodes' : node_list}
            )
            print('Updated node {}.'.format(name))

    def generate_encryption_key(self):
        new_encryption_key = Fernet.generate_key()
        f = Fernet(new_encryption_key)
        nodes_folder_files = os.listdir("nodes")
        node_files = [i for i in nodes_folder_files if i.endswith('.yml')]
        for item in node_files:
            raw_path = Path(item)
            file_stem_name = raw_path.stem
            node_list = self.read_node_list(file_stem_name)
            if node_list is not None:
                #Re-encrypt existing connections.
                nodes_temp = self.get_creds_nodes(node_list)
                for idx in range(len(nodes_temp)):
                    new_node_dict = {
                        "name": "{}".format(nodes_temp[idx]['name']),
                        "protocol": "ssh",
                        "hostname": nodes_temp[idx]['hostname'],
                        "connection_mode": "credentials",
                        "username": f.encrypt(nodes_temp[idx]['username'].encode("utf-8")).decode("utf-8"),
                        "password": f.encrypt(nodes_temp[idx]['password'].encode("utf-8")).decode("utf-8")                      
                    }
                nodes_temp[idx] = new_node_dict
                self.fm.write_yaml(
                    os.path.join(
                        'nodes',
                        '{}.yml'.format(file_stem_name)
                    ),
                    { 'nodes' : nodes_temp}
                )

        with open(
            os.path.join(
                'nodes',
                '{}.bin'.format(CONFIGS.NODE_ENCYRPTION_KEY_FILE)
            ), 
            "wb+") as key_file:
            key_file.write(new_encryption_key)
        
    def _get_encryption_key(self):
        encryption_key = self.fm.read_file(
            os.path.join(
                'nodes',
                '{}.bin'.format(CONFIGS.NODE_ENCYRPTION_KEY_FILE)
            )
        )
        return encryption_key

    def get_creds_nodes(self, node_list: List):
        for node_item in node_list:
            node_item['username'] = self._decrypt_cred(node_item['username'])
            node_item['password'] = self._decrypt_cred(node_item['password'])
        return node_list

    def _decrypt_cred(self, encrypted_cred: str):
        encryption_key = self._get_encryption_key()
        f = Fernet(
            bytes(encryption_key, "utf-8")
        )
        decrypted_message = f.decrypt(
            bytes(encrypted_cred, "utf-8")
        ).decode('UTF-8')
        return decrypted_message

    def _filter_node_by_name(self, name: str, node_list:List):
        filtered = filter(lambda n: n['name'] == name, node_list)
        return list(filtered)

    def _find_by_index(self, node_list: List, node_key: str, node_key_value: str):
        for i, item in enumerate(node_list):
            if item[node_key] == node_key_value:
                return i
        return -1







