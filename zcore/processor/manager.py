from zcore.processor.taskflow_service import TaskflowProcessorService
from zcore.processor.node_service import NodeProcessorService


def Factory(service_name):
    processor_services = {
        "taskflow" : TaskflowProcessorService,
        "node" : NodeProcessorService
    }

    return processor_services[service_name]()