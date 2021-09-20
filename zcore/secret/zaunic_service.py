from abc import ABC, abstractmethod
from zcore.secret.service import SecretsService
import os
import base64
import configparser
from configparser import SafeConfigParser
import codecs
from pathlib import Path
from zcore import logger
from cryptography.fernet import Fernet
from typing import List, Tuple
import CONFIGS

class ZaunicSecretsService(SecretsService):
    def __init__(self):
        self.log = logger.LogMachine()

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
            configs.add_section(section)
        configs.set(section, item_key, str(item_value))
        self._write_config_to_file(
            env,
            config_folder,
            configs
        )

    def _get_configs(
            self, 
            env='dev', 
            config_folder=CONFIGS.SECRETS_CONFIGS_FOLDER
        ):
        parser = SafeConfigParser()
        config_file = Path(
            os.path.join(
                config_folder,
                "{0}.ini".format(env)
            )
        )
        if not config_file.is_file():
            return None
        else:
            with codecs.open(
                config_file, 
                'r',
                encoding='utf-8'
            ) as f:
                parser.readfp(f)
            return parser

    def _get_secrets_with_encryption_key(self, env:str)->Tuple[str, str]:
        secret_list =  self._get_configs(env, CONFIGS.SECRETS_STORE_FOLDER)
        encryption_key = self.get_global_encryption_key(env)
        return secret_list, encryption_key

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

    def _decrypt_secret(
            self, 
            encryption_key: str,
            secret_list: List,
            secret_name: str
        ):
        """
        Retrieve secret from list and decrypt with encryption key.
        """
        f = Fernet(
            bytes(encryption_key, "utf-8")
        )
        secret=None
        if 'secrets' in secret_list:
            if secret_name in secret_list['secrets']:
                secret = f.decrypt(
                    bytes(secret_list['secrets'][secret_name], "utf-8")
                ).decode('UTF-8')
                self.log.log_success(
                    f'{secret_name} : {secret}'
                )
        return secret  

    def get_global_encryption_key(
            self, 
            env: str
        ):
        """
        Description:
        Get the global encryption key used to encrypt secrets in an environment.

        Arguments:
        env -- The environment (dev, pre_prod, prod, stage).
        """
        configs = self._get_configs(env, CONFIGS.SECRETS_CONFIGS_FOLDER)
        if (configs is not None and
            'keys' in configs and
            'global_encyption_key' in configs['keys']
        ):
            return configs['keys']['global_encyption_key']
        else:
            return None

    def set_secret(
            self, 
            env: str,
            item_key: str,
            item_value: str
        ):
        """
        Description:
        Add a new secret to the (local) keystore.

        Arguments:
        env -- The environment (dev, pre_prod, prod, stage).
        item_key -- The key/name for the new secret.
        item_value -- The actual unencrypted secret.

        Notes:
        - The item_value is automatically encrypted internally.
        - Do not send unencrypted item_values over unsecure networks.
        """
        encryption_key = self.get_global_encryption_key(env)
        if encryption_key is not None:
            # Secret can be created.
            f = Fernet(
                bytes(encryption_key, "utf-8")
            )
            token = f.encrypt(bytes(item_value, encoding="utf-8"))
            self._set_config_item(
                env,
                CONFIGS.SECRETS_STORE_FOLDER,
                'secrets',
                item_key,
                "'{0}'".format(
                    token.decode("utf-8")
                )
            )
            self.log.log_success(f'Secret {item_key} has been created/updated in {env} environment.')
        else:
            self.log.log_error(
                f'Secret Creation Failed : Global encryption key for "{env}" environment has not been set.'
            )

    def get_secret(
            self, 
            env: str, 
            secret_name: str, 
            custom_encryption_key:str=None
        )->str:
        """
        Description:
        Retrieve secrets from the (local) keystore.

        Arguments:
        env -- The environment (dev, pre_prod, prod, stage).
        secret_name -- The key/name for the existing secret.

        Notes:
        - Global key (for the environment) is used to read the secret.
        """
        secret_list, encryption_key = self._get_secrets_with_encryption_key(env)
        #Use explicity passed encryption if available.
        if custom_encryption_key is not None:
            encryption_key=custom_encryption_key

        if encryption_key is not None:
            secret = self._decrypt_secret(
                encryption_key,
                secret_list,
                secret_name
            )
            f = Fernet(
                bytes(encryption_key, "utf-8")
            )
        else:
            self.log.log_error(
                f'Secret Retrieval Failed : Global encryption key for "{env}" environment has not been set.'
            )
            self.log.log_error(f'{secret_name} : Unable to retrieve.')
            secret = None
        return secret

    def impute_secrets(self, playbook_data):
        if CONFIGS.SECRETS_KEY in playbook_data:
            secrets = playbook_data['secrets']
            new_secret_dict = {}
            for secret in secrets:
                secrets[secret]['keyvalue'] = self._process_secret(secrets[secret])
                new_secret_dict = { 
                    secrets[secret]['keyname'] : secrets[secret]['keyvalue']
                }
            playbook_data['secrets'] = new_secret_dict
            return playbook_data

    def _process_secret(self, secret:dict):
        secret_source = secret.get('source', "_")
        source_switcher = {
            "zaunic_local" : self.get_local_secret,
            "azure" : self.get_azure_key_vault_secret,
            "aws" : self.get_aws_vault_secret,
            "hashicorp" : self.get_hashicorp_vault_secret,
            "_" : self.handle_missing_source
        }
        return source_switcher[secret['source']](secret['env'], secret['keyname'])

    def get_secret(self, 
            env: str, 
            secret_name: str, 
            custom_encryption_key:str=None
        )->str:
        """
        Description:
        Retrieve secrets from the (local) keystore.

        Arguments:
        env -- The environment (dev, pre_prod, prod, stage).
        secret_name -- The key/name for the existing secret.

        Notes:
        - Global key (for the environment) is used to read the secret.
        """
        secret_list, encryption_key = self._get_secrets_with_encryption_key(env)
        #Use explicity passed encryption if available.
        if custom_encryption_key is not None:
            encryption_key=custom_encryption_key

        if encryption_key is not None:
            secret = self._decrypt_secret(
                encryption_key,
                secret_list,
                secret_name
            )
            f = Fernet(
                bytes(encryption_key, "utf-8")
            )
        else:
            self.log.log_error(
                f'Secret Retrieval Failed : Global encryption key for "{env}" environment has not been set.'
            )
            self.log.log_error(f'{secret_name} : Unable to retrieve.')
            secret = None
        return secret


    def get_local_secret(self, env: str, keyname: str):
        return self.get_secret(env, keyname)

    def get_azure_key_vault_secret(self):
        pass

    def get_aws_vault_secret(self):
        pass

    def get_hashicorp_vault_secret(self):
        pass

    def handle_missing_source(self, env, keyname):
        return ""

        
