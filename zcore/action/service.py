from abc import ABC, abstractmethod

class ActionService(ABC):
    @abstractmethod
    def commit(): pass

class ActionServiceBuilder:
    def __init__(self, action_service: ActionService) -> None:
        self.action_service = action_service

