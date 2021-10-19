import os
from typing import List, Tuple
import base64
import CONFIGS
import configparser
from cryptography.fernet import Fernet
from zcore.secret.zaunic_service import ZaunicSecretsService
from zcore.secret.azure_service import AzureSecretsService


class OrchestratorService():
    def _check_project_state(self):
        keystore_base_path = os.path.join(CONFIGS.SECRETS_STORE_FOLDER)
        
    def _encode_base64_bytes(self, message):
        encoded_bytes = base64.b64encode(bytes(message, 'utf-8'))
        return encoded_bytes

    def _encode_base64_string(self, message):
        encoded_bytes = base64.b64encode(bytes(message, 'utf-8'))
        encoded_message = encoded_bytes.decode("utf-8")
        return encoded_message

    def _write_config_to_file(self, env, config_folder, config):
        with open(
            os.path.join(
                config_folder,
                "{0}.ini".format(env)
            ), 
            'w'
        ) as configfile:
            config.write(configfile)

    def _global_encryption_key_exists(self, env):
        # Check if Global Encryption key exists for the environment.
        # Use this before creating any new secrets.
        pass

    def _set_config_item(
            self, 
            env: str,
            config_folder: str,
            section: str,
            item_key: str,
            item_value: str
        )-> None:
        configs = self._get_configs(env, config_folder)
        if configs is None:
            # Handle non-existent config.
            configs = configparser.ConfigParser()
            configs.optionxform=str
            configs.add_section(section)
        configs.set(section, item_key, str(item_value))
        self._write_config_to_file(
            env,
            config_folder,
            configs
        )

    def set_global_encryption_key(
            self, 
            env: str
        )->None:
        """
        Description:
        Set the encryption key for the environment.

        Arguments:
        env -- The environment (dev, pre_prod, prod, stage).

        """
        old_global_encryption_key = self.get_global_encryption_key(env)
        self._set_config_item(
            env,
            CONFIGS.SECRETS_CONFIGS_FOLDER,
            'keys',
            'global_encyption_key',
            "'{0}'".format(
                Fernet.generate_key().decode("utf-8")
            )
        )

        #Re-encrypt all existing secrets
        secrets_list, _ = self._get_secrets_with_encryption_key(env)
        self._re_encrypt_secrets(env, secrets_list, old_global_encryption_key)
        
        self.log.log_success(
                f'Encyption key for {env} environment has been created/updated.'
        )
        return None

    def _re_encrypt_secrets(
            self, 
            env: str, 
            secrets_list: list, 
            old_encrypt_key: str
        ) -> None:
        """
        Re-encrypt keys with new encryption key.
        """
        if secrets_list is not None:
            for secret in secrets_list['secrets']:
                existing_val = self.get_secret(env, secret, old_encrypt_key)
                self.add_secret(env, secret, existing_val)

  

    def impute_secrets(self, taskflow_data):
        if CONFIGS.SECRETS_KEY in taskflow_data:
            secrets = taskflow_data['secrets']
            new_secret_dict = {}
            for secret in secrets:
                secrets[secret]['keyvalue'] = self._process_secret(secrets[secret])
                new_secret_dict = { 
                    secrets[secret]['keyname'] : secrets[secret]['keyvalue']
                }
            taskflow_data['secrets'] = new_secret_dict
            return taskflow_data

    def _process_secret(self, secret:dict):
        source_switcher = {
            "zaunic_local" : self.get_local_secret,
            "azure" : self.get_azure_key_vault_secret,
            "aws" : self.get_aws_vault_secret,
            "hashicorp" : self.get_hashicorp_vault_secret,
            "_" : self.handle_missing_source
        }
        return source_switcher[secret['source']](secret)

    def get_local_secret(self, secret):
        zaunic_secrets_service = ZaunicSecretsService()
        return zaunic_secrets_service.get_secret(secret['env'], secret['keyname'])

    def get_azure_key_vault_secret(self, secret):
        az = AzureSecretsService()
        can_get_secret = az.can_get_secret(
            secret['instance'], 
            secret['env'], 
            secret['keyname']
            )
        if can_get_secret==False:
            zaunic_secrets_service = ZaunicSecretsService()
            secret = zaunic_secrets_service.get_secret(secret['env'], secret['keyname'])
        else:
            client_id = az.get_client_credential('client_id', secret['instance'], secret['env'])
            client_secret = az.get_client_credential('client_secret', secret['instance'], secret['env'])
            tenant_id = az.get_client_credential('tenant_id', secret['instance'], secret['env'])
            secret = az.get_secret_from_keyvault(
                secret['instance'],
                client_id,
                client_secret,
                tenant_id,
                secret['keyname']
            )
        return secret

    def get_aws_vault_secret(self):
        pass

    def get_hashicorp_vault_secret(self):
        pass

    def handle_missing_source(self, env, keyname):
        return ""