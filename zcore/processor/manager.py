from zcore.processor.playbook_service import PlaybookProcessorService
from zcore.processor.node_service import NodeProcessorService


def Factory(service_name):
    processor_services = {
        "playbook" : PlaybookProcessorService,
        "node" : NodeProcessorService
    }

    return processor_services[service_name]()