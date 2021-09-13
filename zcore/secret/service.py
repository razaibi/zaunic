from abc import ABC, abstractmethod

class SecretsService(ABC):
    @abstractmethod
    def set_secret(env: str, item_key: str, item_value: str): pass

    @abstractmethod
    def get_secret(env: str, item_key: str): pass


class SecretsServiceBuilder:
    def __init__(self, secrets_service: SecretsService) -> None:
        self.secrets_service = secrets_service

