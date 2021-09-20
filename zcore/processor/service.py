from abc import ABC, abstractmethod

class ProcessorService(ABC):
    @abstractmethod
    def read_list(): pass

class ProcessorServiceBuilder:
    def __init__(self, processor_service: ProcessorService) -> None:
        self.processor_service = processor_service

