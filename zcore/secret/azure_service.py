import os
from typing import Dict, List, Tuple
from zcore import logger
from zcore.secret.service import SecretsService
from zcore.secret.zaunic_service import ZaunicSecretsService
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

class AzureSecretsService(SecretsService):
    def __init__(self):
        self.log = logger.LogMachine()

    def can_get_secret(self, instance:str, env:str, keyname: str):
        client_id = self.get_client_credential('client_id', instance, env)
        client_secret = self.get_client_credential('client_secret', instance, env)
        tenant_id = self.get_client_credential('tenant_id', instance, env)
        if None in (client_id, client_secret, tenant_id):
            return False
        else:
            return True

    def get_secret(self, instance:str, env:str, keyname: str):
        client_id = self.get_client_credential('client_id', instance, env)
        client_secret = self.get_client_credential('client_secret', instance, env)
        tenant_id = self.get_client_credential('tenant_id', instance, env)
        if None in (client_id, client_secret, tenant_id):
            return None
        secret = None
        if None not in (client_id, client_secret, tenant_id):
            secret = self.get_secret_from_keyvault(
                instance,
                client_id,
                client_secret,
                tenant_id,
                keyname
            )
        return secret

    def get_secret_from_keyvault(self, 
            instance:str, 
            client_id: str,
            client_secret: str,
            tenant_id: str, 
            keyname:str
        ):
        """
        Description:
        Create a client to access credentials from Azure Key Vault.

        Arguments:
        instance -- Name of keyvault
        client_credentials -- Dictionary containing client id, client secret and tenant id.
        """
        
        client_credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

        secret_client = SecretClient(
            vault_url='https://{}.vault.azure.net/'.format(instance),
            credential=client_credential,
            logging_enable=False
        )
        secret = secret_client.get_secret(keyname)
        return secret.value

    def get_client_credential(self, credential_type:str, instance:str, env:str):
        """
        Description:
        Check if credential for Azure Client is defined as an environment variable.
        If not, check the Zaunic Secret store to retrieve credential value.

        Arguments:
        credential_type -- The credential type
        (one from tenant_id, client_id, client_secret or subscription_id).
        """
        credential_keyname = 'azure_{}_{}_{}'.format(
            instance,
            env,
            credential_type
        )
        credential_env_variable = os.getenv(credential_keyname)
        if credential_env_variable is not None:
            credential_value = credential_env_variable
        else:
            zaunic_secrets_service = ZaunicSecretsService()
            credential_value = zaunic_secrets_service.get_secret(env, credential_keyname)
        return credential_value


    def get_client_credential_keyname(self, credential_type:str, instance:str, env:str):
        credential_keyname = '{}'.format(
            credential_type.lower()
        )
        return credential_keyname


    def set_secret(self, env: str, item_key: str, item_value: str): 
        pass
